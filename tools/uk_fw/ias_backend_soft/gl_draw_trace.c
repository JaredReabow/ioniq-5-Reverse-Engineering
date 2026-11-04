/*
 * gl_draw_trace — capture the draw path of a Qt application that reaches GL through the
 * function table, together with the vertex state that governs it.
 *
 * Why this shape
 * --------------
 * The application resolves only three entry points through the loader — measured with
 * gl_loader_probe.c:
 *
 *     glRenderbufferStorageMultisampleEXT
 *     glFramebufferTexture2DMultisampleEXT
 *     glDrawElementsBaseVertex
 *
 * Everything else binds by exported symbol (this project's upload tracer already intercepts
 * glTexImage2D, glPixelStorei and glTexParameteri successfully). So the draw itself needs the
 * loader, and the state around it does not. Splitting the instrument this way is simpler and
 * more robust than routing every call through the loader.
 *
 * What it records, per draw: mode, count, index type, the bound array/element buffers, the
 * bound texture, and the attribute pointers registered through glVertexAttribPointer. The
 * attribute records are what would reveal a per-row lateral offset of a few texels, which is
 * the measured defect: three pixels of shear per row in the captured frame.
 *
 * Bounded to a fixed number of draws so a long session cannot fill the guest's /tmp.
 *
 * Research instrument: every call is forwarded unchanged.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define LOG_PATH "/tmp/gl-draw.log"
#define MAX_DRAWS 120
#define MAX_ATTRS 16
#define MAX_TEX 16

typedef unsigned int GLenum;
typedef unsigned char GLboolean;
typedef unsigned int GLuint;
typedef int GLint;
typedef int GLsizei;
typedef ptrdiff_t GLsizeiptr;
typedef ptrdiff_t GLintptr;
typedef float GLfloat;
typedef char GLchar;

struct attr {
	GLuint index;
	GLint size;
	GLenum type;
	GLboolean normalized;
	GLsizei stride;
	const void *pointer;
	int active;
};

static struct attr attrs[MAX_ATTRS];
static GLuint bound_array_buffer;
static GLuint bound_element_buffer;
static GLuint bound_textures[MAX_TEX];
static int draws;
static int logfd = -2;

static void put(char **p, const char *s)
{
	while (*s)
		*(*p)++ = *s++;
}

static void putn(char **p, long long v)
{
	char tmp[24];
	int n = 0, i;

	if (v < 0) {
		*(*p)++ = '-';
		v = -v;
	}
	if (v == 0)
		tmp[n++] = '0';
	while (v > 0 && n < 22) {
		tmp[n++] = (char)('0' + v % 10);
		v /= 10;
	}
	for (i = n - 1; i >= 0; i--)
		*(*p)++ = tmp[i];
}

static void emit_line(char *line, char *p)
{
	if (logfd == -2)
		logfd = open(LOG_PATH, O_WRONLY | O_CREAT | O_APPEND, 0644);
	if (logfd >= 0)
		(void)!write(logfd, line, (size_t)(p - line));
}

/* ---- exported-symbol hooks: state only, no drawing ---- */

void glVertexAttribPointer(GLuint index, GLint size, GLenum type,
			   GLboolean normalized, GLsizei stride, const void *pointer)
{
	static void (*real)(GLuint, GLint, GLenum, GLboolean, GLsizei, const void *);

	if (index < MAX_ATTRS) {
		attrs[index].index = index;
		attrs[index].size = size;
		attrs[index].type = type;
		attrs[index].normalized = normalized;
		attrs[index].stride = stride;
		attrs[index].pointer = pointer;
		attrs[index].active = 1;
	}
	if (!real)
		real = dlsym(RTLD_NEXT, "glVertexAttribPointer");
	if (real)
		real(index, size, type, normalized, stride, pointer);
}

void glBindBuffer(GLenum target, GLuint buffer)
{
	static void (*real)(GLenum, GLuint);

	if (target == 0x8892)		/* GL_ARRAY_BUFFER */
		bound_array_buffer = buffer;
	else if (target == 0x8893)	/* GL_ELEMENT_ARRAY_BUFFER */
		bound_element_buffer = buffer;

	if (!real)
		real = dlsym(RTLD_NEXT, "glBindBuffer");
	if (real)
		real(target, buffer);
}

void glBindTexture(GLenum target, GLuint texture)
{
	static void (*real)(GLenum, GLuint);

	if (texture < MAX_TEX)
		bound_textures[texture] = texture;

	if (!real)
		real = dlsym(RTLD_NEXT, "glBindTexture");
	if (real)
		real(target, texture);
}

/* ---- the draw itself, reached through the loader ---- */

static void (*real_draw_base_vertex)(GLenum, GLsizei, GLenum, const void *, GLint);

static void
trace_draw_base_vertex(GLenum mode, GLsizei count, GLenum type,
		       const void *indices, GLint basevertex)
{
	char line[512];
	char *p = line;
	int i;

	if (draws < MAX_DRAWS) {
		put(&p, "draw mode=");
		putn(&p, (long long)mode);
		put(&p, " count=");
		putn(&p, (long long)count);
		put(&p, " type=");
		putn(&p, (long long)type);
		put(&p, " basevertex=");
		putn(&p, (long long)basevertex);
		put(&p, " elem_buf=");
		putn(&p, (long long)bound_element_buffer);
		put(&p, " array_buf=");
		putn(&p, (long long)bound_array_buffer);
		put(&p, " indices=");
		putn(&p, (long long)(intptr_t)indices);
		put(&p, "\n");
		emit_line(line, p);

		for (i = 0; i < MAX_ATTRS; i++) {
			if (!attrs[i].active)
				continue;
			p = line;
			put(&p, "  attr idx=");
			putn(&p, (long long)attrs[i].index);
			put(&p, " size=");
			putn(&p, (long long)attrs[i].size);
			put(&p, " type=");
			putn(&p, (long long)attrs[i].type);
			put(&p, " stride=");
			putn(&p, (long long)attrs[i].stride);
			put(&p, " ptr=");
			putn(&p, (long long)(intptr_t)attrs[i].pointer);
			put(&p, "\n");
			emit_line(line, p);
		}
		draws++;
	}

	if (real_draw_base_vertex)
		real_draw_base_vertex(mode, count, type, indices, basevertex);
}

void *eglGetProcAddress(const char *name)
{
	static void *(*real)(const char *);
	void *fn;

	if (!real)
		real = dlsym(RTLD_NEXT, "eglGetProcAddress");
	fn = real ? real(name) : NULL;

	if (name != NULL && strcmp(name, "glDrawElementsBaseVertex") == 0) {
		char line[128];
		char *q = line;
		/* Marker: proves the wrapper replaced the real pointer. Without it an empty
		 * draw log is ambiguous between "not wrapped" and "not drawn". */
		real_draw_base_vertex = fn;
		put(&q, "wrap installed for glDrawElementsBaseVertex, real=");
		putn(&q, (long long)(intptr_t)fn);
		put(&q, "\n");
		emit_line(line, q);
		return (void *)trace_draw_base_vertex;
	}
	return fn;
}

/*
 * The exported draw entry points.
 * ------------------------------
 * The loader wrapper above installed successfully but recorded zero draws, which means this
 * application does not reach glDrawElementsBaseVertex through the loader at the time it draws:
 * the three loader lookups observed in gl_loader_probe.c evidently belong to a different
 * process in the same boot. The draw this application actually issues therefore arrives through
 * an exported symbol, which is interceptable directly. Both paths are covered so the log cannot
 * be empty for the wrong reason.
 */
void glDrawElements(GLenum mode, GLsizei count, GLenum type, const void *indices)
{
	static void (*real)(GLenum, GLsizei, GLenum, const void *);

	if (draws < MAX_DRAWS) {
		char line[320];
		char *p = line;
		put(&p, "drawE mode=");
		putn(&p, (long long)mode);
		put(&p, " count=");
		putn(&p, (long long)count);
		put(&p, " type=");
		putn(&p, (long long)type);
		put(&p, " elem_buf=");
		putn(&p, (long long)bound_element_buffer);
		put(&p, " array_buf=");
		putn(&p, (long long)bound_array_buffer);
		put(&p, " indices=");
		putn(&p, (long long)(intptr_t)indices);
		put(&p, "\n");
		emit_line(line, p);
		for (int i = 0; i < MAX_ATTRS; i++) {
			if (!attrs[i].active)
				continue;
			p = line;
			put(&p, "  attr idx=");
			putn(&p, (long long)attrs[i].index);
			put(&p, " size=");
			putn(&p, (long long)attrs[i].size);
			put(&p, " type=");
			putn(&p, (long long)attrs[i].type);
			put(&p, " stride=");
			putn(&p, (long long)attrs[i].stride);
			put(&p, " ptr=");
			putn(&p, (long long)(intptr_t)attrs[i].pointer);
			put(&p, "\n");
			emit_line(line, p);
		}
		draws++;
	}

	if (!real)
		real = dlsym(RTLD_NEXT, "glDrawElements");
	if (real)
		real(mode, count, type, indices);
}

void glDrawArrays(GLenum mode, GLint first, GLsizei count)
{
	static void (*real)(GLenum, GLint, GLsizei);

	if (draws < MAX_DRAWS) {
		char line[192];
		char *p = line;
		put(&p, "drawA mode=");
		putn(&p, (long long)mode);
		put(&p, " first=");
		putn(&p, (long long)first);
		put(&p, " count=");
		putn(&p, (long long)count);
		put(&p, "\n");
		emit_line(line, p);
		draws++;
	}

	if (!real)
		real = dlsym(RTLD_NEXT, "glDrawArrays");
	if (real)
		real(mode, first, count);
}

/*
 * Vertex payloads.
 * ---------------
 * The attribute trace showed interleaved vertices in array buffer 3, so the coordinates
 * themselves arrive through glBufferData / glBufferSubData. Dumping the first kilobyte of each
 * upload is what makes the measured question answerable: do the texture coordinates of two
 * adjacent rows differ by three texels?
 */
static int bufdumps;

static void dump_buffer(const char *what, GLsizeiptr size, const void *data)
{
	char line[128];
	char *p = line;
	char path[64];
	int fd, idx;

	if (data == NULL || size <= 0)
		return;
	if (bufdumps >= 6)
		return;
	idx = bufdumps++;

	snprintf(path, sizeof path, "/tmp/gl-buf-%d.bin", idx);
	fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (fd >= 0) {
		size_t n = (size_t)(size > 1024 ? 1024 : size);
		(void)!write(fd, data, n);
		close(fd);
	}

	p = line;
	put(&p, what);
	put(&p, " size=");
	putn(&p, (long long)size);
	put(&p, " dumped=");
	putn(&p, (long long)idx);
	put(&p, "\n");
	emit_line(line, p);
}

void glBufferData(GLenum target, GLsizeiptr size, const void *data, GLenum usage)
{
	static void (*real)(GLenum, GLsizeiptr, const void *, GLenum);

	dump_buffer("glBufferData", size, data);
	if (!real)
		real = dlsym(RTLD_NEXT, "glBufferData");
	if (real)
		real(target, size, data, usage);
}

void glBufferSubData(GLenum target, GLintptr offset, GLsizeiptr size, const void *data)
{
	static void (*real)(GLenum, GLintptr, GLsizeiptr, const void *);

	dump_buffer("glBufferSubData", size, data);
	if (!real)
		real = dlsym(RTLD_NEXT, "glBufferSubData");
	if (real)
		real(target, offset, size, data);
}

/*
 * Shader sources.
 * --------------
 * The attribute trace showed position at offset 0 and a second pair at offset 8, but the decoded
 * values do not pair the way a fixed-function quad would: corners carry other corners' texture
 * coordinates. Whether that is a fault or simply a shader computing coordinates from another
 * attribute cannot be decided without reading the shader. glShaderSource carries it.
 */
/*
 * Experiment: rewrite the quad shader's varying assignment at upload time.
 *
 * The recovered shader is:
 *     gl_Position = position;
 *     outTexCoords = texCoords.xy;
 * and the captured buffer pairs corners inconsistently, which would mirror and shear a
 * full-screen quad. Two rewrites are offered so the picture itself can say which mapping is
 * wrong:
 *     IAS_SHADER_FIX=swap   -> outTexCoords = texCoords.yx;
 *     IAS_SHADER_FIX=flipu  -> outTexCoords = vec2(-texCoords.x, texCoords.y);
 * If either produces a correct background, the missing transform is identified. If neither
 * changes anything, the fault is not in this assignment.
 */
static int shader_fix_mode(void)
{
	static int cached = -1;
	const char *v;

	if (cached >= 0)
		return cached;
	/* Marker files, because the launcher rebuilds its children's environment and an
	 * environment variable cannot reach the application. */
	if (access("/tmp/shader-fix-swap", F_OK) == 0) {
		cached = 1;
		return cached;
	}
	if (access("/tmp/shader-fix-flipu", F_OK) == 0) {
		cached = 2;
		return cached;
	}
	if (access("/tmp/shader-fix-norm", F_OK) == 0) {
		cached = 3;
		return cached;
	}
	if (access("/tmp/shader-fix-flipv", F_OK) == 0) {
		cached = 4;
		return cached;
	}
	v = getenv("IAS_SHADER_FIX");
	if (v == NULL)
		cached = 0;
	else if (strcmp(v, "swap") == 0)
		cached = 1;
	else if (strcmp(v, "flipu") == 0)
		cached = 2;
	else
		cached = 0;
	return cached;
}

static const char *rewrite_shader(const char *src)
{
	static char buf[8192];
	const char *needle = "outTexCoords = texCoords.xy;";
	const char *at;
	size_t head;

	if (src == NULL)
		return src;
	at = strstr(src, needle);
	if (at == NULL || shader_fix_mode() == 0)
		return src;

	head = (size_t)(at - src);
	if (head + 256 > sizeof buf)
		return src;

	memcpy(buf, src, head);
	buf[head] = 0;
	if (shader_fix_mode() == 1)
		strcat(buf, "outTexCoords = texCoords.yx;");
	else if (shader_fix_mode() == 2)
		strcat(buf, "outTexCoords = vec2(-texCoords.x, texCoords.y);");
	else if (shader_fix_mode() == 3)
		/* The captured quads carry clip-space positions and coordinates in the same
		 * -1..1 range; a texture expects 0..1. */
		strcat(buf, "outTexCoords = vec2((texCoords.x + 1.0) * 0.5, "
			    "(texCoords.y + 1.0) * 0.5);");
	else
		strcat(buf, "outTexCoords = vec2(texCoords.x, -texCoords.y);");
	strcat(buf, at + strlen(needle));
	return buf;
}

static int shaderdumps;

void glShaderSource(GLuint shader, GLsizei count, const GLchar *const *string,
		    const GLint *length)
{
	static void (*real)(GLuint, GLsizei, const GLchar *const *, const GLint *);
	char path[64];
	int fd, i;

	if (count > 0 && string != NULL) {
		const char *rw = rewrite_shader(string[0]);
		if (rw != string[0]) {
			GLchar *repl[1];
			GLint len[1];
			repl[0] = (GLchar *)rw;
			len[0] = (GLint)strlen(rw);
			(void)count;
			if (!real)
				real = dlsym(RTLD_NEXT, "glShaderSource");
			if (real)
				real(shader, 1, repl, len);
			return;
		}
	}

	if (shaderdumps < 8 && count > 0 && string != NULL) {
		snprintf(path, sizeof path, "/tmp/gl-shader-%d.txt", shaderdumps++);
		fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
		if (fd >= 0) {
			for (i = 0; i < count; i++) {
				const char *t = string[i];
				size_t n;
				if (t == NULL)
					continue;
				n = (length && length[i] > 0) ? (size_t)length[i]
							      : strlen(t);
				(void)!write(fd, t, n);
			}
			(void)!write(fd, "\n", 1);
			close(fd);
		}
	}

	if (!real)
		real = dlsym(RTLD_NEXT, "glShaderSource");
	if (real)
		real(shader, count, string, length);
}

