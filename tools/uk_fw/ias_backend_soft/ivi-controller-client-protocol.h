/*
 * Interface definitions reconstructed from the vendor Gen5W build of
 * weston 1.10 (ivi-controller.so). The protocol itself is the GENIVI
 * IVI layer management controller interface (DENSO CORPORATION / BMW Car IT
 * GmbH, MIT).
 */

#ifndef IVI_CONTROLLER_CLIENT_PROTOCOL_H
#define IVI_CONTROLLER_CLIENT_PROTOCOL_H

#ifdef  __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include "wayland-client.h"

struct wl_client;
struct wl_resource;

struct ivi_controller;
struct ivi_controller_layer;
struct ivi_controller_screen;
struct ivi_controller_surface;
struct ivi_share;
struct ivi_share_surface;

extern const struct wl_interface ivi_controller_interface;
extern const struct wl_interface ivi_controller_layer_interface;
extern const struct wl_interface ivi_controller_surface_interface;
extern const struct wl_interface ivi_controller_screen_interface;
extern const struct wl_interface ivi_share_interface;
extern const struct wl_interface ivi_share_surface_interface;

/**
 * ivi_controller - layer management controller
 * @screen: (none)
 * @layer: (none)
 * @surface: (none)
 * @error: (none)
 *
 * 
 */
struct ivi_controller_listener {
	/**
	 * screen - (none)
	 * @id_screen: (none)
	 * @id: (none)
	 */
	void (*screen)(void *data,
		       struct ivi_controller *ivi_controller,
		       uint32_t id_screen,
		       struct ivi_controller_screen *id);
	/**
	 * layer - (none)
	 * @id_layer: (none)
	 */
	void (*layer)(void *data,
		      struct ivi_controller *ivi_controller,
		      uint32_t id_layer);
	/**
	 * surface - (none)
	 * @id_surface: (none)
	 */
	void (*surface)(void *data,
			struct ivi_controller *ivi_controller,
			uint32_t id_surface);
	/**
	 * error - (none)
	 * @object_id: (none)
	 * @object_type: (none)
	 * @error: (none)
	 * @message: (none)
	 */
	void (*error)(void *data,
		      struct ivi_controller *ivi_controller,
		      int32_t object_id,
		      int32_t object_type,
		      int32_t error,
		      const char *message);
};

static inline int
ivi_controller_add_listener(struct ivi_controller *ivi_controller,
			    const struct ivi_controller_listener *listener, void *data)
{
	return wl_proxy_add_listener((struct wl_proxy *) ivi_controller,
				     (void (**)(void)) listener, data);
}

#define IVI_CONTROLLER_COMMIT_CHANGES	0
#define IVI_CONTROLLER_LAYER_CREATE	1
#define IVI_CONTROLLER_SURFACE_CREATE	2

#define IVI_CONTROLLER_COMMIT_CHANGES_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_CREATE_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_CREATE_SINCE_VERSION	1

static inline void
ivi_controller_set_user_data(struct ivi_controller *ivi_controller, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_controller, user_data);
}

static inline void *
ivi_controller_get_user_data(struct ivi_controller *ivi_controller)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_controller);
}

static inline uint32_t
ivi_controller_get_version(struct ivi_controller *ivi_controller)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_controller);
}

static inline void
ivi_controller_destroy(struct ivi_controller *ivi_controller)
{
	wl_proxy_destroy((struct wl_proxy *) ivi_controller);
}

static inline void
ivi_controller_commit_changes(struct ivi_controller *ivi_controller)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller,
			 IVI_CONTROLLER_COMMIT_CHANGES);
}

static inline struct ivi_controller_layer *
ivi_controller_layer_create(struct ivi_controller *ivi_controller, uint32_t id_layer, int32_t width, int32_t height)
{
	struct wl_proxy *id;

	id = wl_proxy_marshal_constructor((struct wl_proxy *) ivi_controller,
			 IVI_CONTROLLER_LAYER_CREATE, &ivi_controller_layer_interface, id_layer, width, height, NULL);

	return (struct ivi_controller_layer *) id;
}

static inline struct ivi_controller_surface *
ivi_controller_surface_create(struct ivi_controller *ivi_controller, uint32_t id_surface)
{
	struct wl_proxy *id;

	id = wl_proxy_marshal_constructor((struct wl_proxy *) ivi_controller,
			 IVI_CONTROLLER_SURFACE_CREATE, &ivi_controller_surface_interface, id_surface, NULL);

	return (struct ivi_controller_surface *) id;
}

struct ivi_controller_layer_listener {
	/**
	 * visibility - (none)
	 * @is_visible: (none)
	 */
	void (*visibility)(void *data,
			   struct ivi_controller_layer *ivi_controller_layer,
			   int32_t is_visible);
	/**
	 * opacity - (none)
	 * @opacity: (none)
	 */
	void (*opacity)(void *data,
			struct ivi_controller_layer *ivi_controller_layer,
			wl_fixed_t opacity);
	/**
	 * source_rectangle - (none)
	 * @x: (none)
	 * @y: (none)
	 * @width: (none)
	 * @height: (none)
	 */
	void (*source_rectangle)(void *data,
				 struct ivi_controller_layer *ivi_controller_layer,
				 int32_t x,
				 int32_t y,
				 int32_t width,
				 int32_t height);
	/**
	 * destination_rectangle - (none)
	 * @x: (none)
	 * @y: (none)
	 * @width: (none)
	 * @height: (none)
	 */
	void (*destination_rectangle)(void *data,
				      struct ivi_controller_layer *ivi_controller_layer,
				      int32_t x,
				      int32_t y,
				      int32_t width,
				      int32_t height);
	/**
	 * configuration - (none)
	 * @width: (none)
	 * @height: (none)
	 */
	void (*configuration)(void *data,
			      struct ivi_controller_layer *ivi_controller_layer,
			      int32_t width,
			      int32_t height);
	/**
	 * orientation - (none)
	 * @orientation: (none)
	 */
	void (*orientation)(void *data,
			    struct ivi_controller_layer *ivi_controller_layer,
			    int32_t orientation);
	/**
	 * screen - (none)
	 * @id_screen: (none)
	 */
	void (*screen)(void *data,
		       struct ivi_controller_layer *ivi_controller_layer,
		       void *id_screen);
	/**
	 * destroyed - (none)
	 */
	void (*destroyed)(void *data,
			  struct ivi_controller_layer *ivi_controller_layer);
};

static inline int
ivi_controller_layer_add_listener(struct ivi_controller_layer *ivi_controller_layer,
				  const struct ivi_controller_layer_listener *listener, void *data)
{
	return wl_proxy_add_listener((struct wl_proxy *) ivi_controller_layer,
				     (void (**)(void)) listener, data);
}

#define IVI_CONTROLLER_LAYER_SET_VISIBILITY	0
#define IVI_CONTROLLER_LAYER_SET_OPACITY	1
#define IVI_CONTROLLER_LAYER_SET_SOURCE_RECTANGLE	2
#define IVI_CONTROLLER_LAYER_SET_DESTINATION_RECTANGLE	3
#define IVI_CONTROLLER_LAYER_SET_CONFIGURATION	4
#define IVI_CONTROLLER_LAYER_SET_ORIENTATION	5
#define IVI_CONTROLLER_LAYER_SCREENSHOT	6
#define IVI_CONTROLLER_LAYER_CLEAR_SURFACES	7
#define IVI_CONTROLLER_LAYER_ADD_SURFACE	8
#define IVI_CONTROLLER_LAYER_REMOVE_SURFACE	9
#define IVI_CONTROLLER_LAYER_SET_RENDER_ORDER	10
#define IVI_CONTROLLER_LAYER_DESTROY	11

#define IVI_CONTROLLER_LAYER_SET_VISIBILITY_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_SET_OPACITY_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_SET_SOURCE_RECTANGLE_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_SET_DESTINATION_RECTANGLE_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_SET_CONFIGURATION_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_SET_ORIENTATION_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_SCREENSHOT_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_CLEAR_SURFACES_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_ADD_SURFACE_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_REMOVE_SURFACE_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_SET_RENDER_ORDER_SINCE_VERSION	1
#define IVI_CONTROLLER_LAYER_DESTROY_SINCE_VERSION	1

static inline void
ivi_controller_layer_set_user_data(struct ivi_controller_layer *ivi_controller_layer, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_controller_layer, user_data);
}

static inline void *
ivi_controller_layer_get_user_data(struct ivi_controller_layer *ivi_controller_layer)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_controller_layer);
}

static inline uint32_t
ivi_controller_layer_get_version(struct ivi_controller_layer *ivi_controller_layer)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_controller_layer);
}

static inline void
ivi_controller_layer_set_visibility(struct ivi_controller_layer *ivi_controller_layer, uint32_t is_visible)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SET_VISIBILITY, is_visible);
}

static inline void
ivi_controller_layer_set_opacity(struct ivi_controller_layer *ivi_controller_layer, wl_fixed_t opacity)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SET_OPACITY, opacity);
}

static inline void
ivi_controller_layer_set_source_rectangle(struct ivi_controller_layer *ivi_controller_layer, int32_t x, int32_t y, int32_t width, int32_t height)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SET_SOURCE_RECTANGLE, x, y, width, height);
}

static inline void
ivi_controller_layer_set_destination_rectangle(struct ivi_controller_layer *ivi_controller_layer, int32_t x, int32_t y, int32_t width, int32_t height)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SET_DESTINATION_RECTANGLE, x, y, width, height);
}

static inline void
ivi_controller_layer_set_configuration(struct ivi_controller_layer *ivi_controller_layer, int32_t width, int32_t height)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SET_CONFIGURATION, width, height);
}

static inline void
ivi_controller_layer_set_orientation(struct ivi_controller_layer *ivi_controller_layer, int32_t orientation)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SET_ORIENTATION, orientation);
}

static inline void
ivi_controller_layer_screenshot(struct ivi_controller_layer *ivi_controller_layer, const char *output)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SCREENSHOT, output);
}

static inline void
ivi_controller_layer_clear_surfaces(struct ivi_controller_layer *ivi_controller_layer)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_CLEAR_SURFACES);
}

static inline void
ivi_controller_layer_add_surface(struct ivi_controller_layer *ivi_controller_layer, struct ivi_controller_surface *id_surface)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_ADD_SURFACE, id_surface);
}

static inline void
ivi_controller_layer_remove_surface(struct ivi_controller_layer *ivi_controller_layer, struct ivi_controller_surface *id_surface)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_REMOVE_SURFACE, id_surface);
}

static inline void
ivi_controller_layer_set_render_order(struct ivi_controller_layer *ivi_controller_layer, struct wl_array *id_surfaces)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_SET_RENDER_ORDER, id_surfaces);
}

static inline void
ivi_controller_layer_destroy(struct ivi_controller_layer *ivi_controller_layer, int32_t id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_layer,
			 IVI_CONTROLLER_LAYER_DESTROY, id);
}

struct ivi_controller_surface_listener {
	/**
	 * visibility - (none)
	 * @is_visible: (none)
	 */
	void (*visibility)(void *data,
			   struct ivi_controller_surface *ivi_controller_surface,
			   int32_t is_visible);
	/**
	 * opacity - (none)
	 * @opacity: (none)
	 */
	void (*opacity)(void *data,
			struct ivi_controller_surface *ivi_controller_surface,
			wl_fixed_t opacity);
	/**
	 * source_rectangle - (none)
	 * @x: (none)
	 * @y: (none)
	 * @width: (none)
	 * @height: (none)
	 */
	void (*source_rectangle)(void *data,
				 struct ivi_controller_surface *ivi_controller_surface,
				 int32_t x,
				 int32_t y,
				 int32_t width,
				 int32_t height);
	/**
	 * destination_rectangle - (none)
	 * @x: (none)
	 * @y: (none)
	 * @width: (none)
	 * @height: (none)
	 */
	void (*destination_rectangle)(void *data,
				      struct ivi_controller_surface *ivi_controller_surface,
				      int32_t x,
				      int32_t y,
				      int32_t width,
				      int32_t height);
	/**
	 * configuration - (none)
	 * @width: (none)
	 * @height: (none)
	 */
	void (*configuration)(void *data,
			      struct ivi_controller_surface *ivi_controller_surface,
			      int32_t width,
			      int32_t height);
	/**
	 * orientation - (none)
	 * @orientation: (none)
	 */
	void (*orientation)(void *data,
			    struct ivi_controller_surface *ivi_controller_surface,
			    int32_t orientation);
	/**
	 * pixelformat - (none)
	 * @pixelformat: (none)
	 */
	void (*pixelformat)(void *data,
			    struct ivi_controller_surface *ivi_controller_surface,
			    int32_t pixelformat);
	/**
	 * layer - (none)
	 * @id_layer: (none)
	 */
	void (*layer)(void *data,
		      struct ivi_controller_surface *ivi_controller_surface,
		      struct ivi_controller_layer *id_layer);
	/**
	 * stats - (none)
	 * @number_of_frames: (none)
	 * @frame_counter: (none)
	 * @frame_delta_nsec: (none)
	 * @last_frame_delta_nsec: (none)
	 * @process_name: (none)
	 */
	void (*stats)(void *data,
		      struct ivi_controller_surface *ivi_controller_surface,
		      uint32_t number_of_frames,
		      uint32_t frame_counter,
		      uint32_t frame_delta_nsec,
		      uint32_t last_frame_delta_nsec,
		      const char *process_name);
	/**
	 * destroyed - (none)
	 */
	void (*destroyed)(void *data,
			  struct ivi_controller_surface *ivi_controller_surface);
	/**
	 * content - (none)
	 * @content_state: (none)
	 */
	void (*content)(void *data,
			struct ivi_controller_surface *ivi_controller_surface,
			int32_t content_state);
};

static inline int
ivi_controller_surface_add_listener(struct ivi_controller_surface *ivi_controller_surface,
				    const struct ivi_controller_surface_listener *listener, void *data)
{
	return wl_proxy_add_listener((struct wl_proxy *) ivi_controller_surface,
				     (void (**)(void)) listener, data);
}

#define IVI_CONTROLLER_SURFACE_SET_VISIBILITY	0
#define IVI_CONTROLLER_SURFACE_SET_OPACITY	1
#define IVI_CONTROLLER_SURFACE_SET_SOURCE_RECTANGLE	2
#define IVI_CONTROLLER_SURFACE_SET_DESTINATION_RECTANGLE	3
#define IVI_CONTROLLER_SURFACE_SET_CONFIGURATION	4
#define IVI_CONTROLLER_SURFACE_SET_ORIENTATION	5
#define IVI_CONTROLLER_SURFACE_SCREENSHOT	6
#define IVI_CONTROLLER_SURFACE_SEND_STATS	7
#define IVI_CONTROLLER_SURFACE_DESTROY	8

#define IVI_CONTROLLER_SURFACE_SET_VISIBILITY_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_SET_OPACITY_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_SET_SOURCE_RECTANGLE_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_SET_DESTINATION_RECTANGLE_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_SET_CONFIGURATION_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_SET_ORIENTATION_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_SCREENSHOT_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_SEND_STATS_SINCE_VERSION	1
#define IVI_CONTROLLER_SURFACE_DESTROY_SINCE_VERSION	1

static inline void
ivi_controller_surface_set_user_data(struct ivi_controller_surface *ivi_controller_surface, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_controller_surface, user_data);
}

static inline void *
ivi_controller_surface_get_user_data(struct ivi_controller_surface *ivi_controller_surface)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_controller_surface);
}

static inline uint32_t
ivi_controller_surface_get_version(struct ivi_controller_surface *ivi_controller_surface)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_controller_surface);
}

static inline void
ivi_controller_surface_set_visibility(struct ivi_controller_surface *ivi_controller_surface, uint32_t is_visible)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SET_VISIBILITY, is_visible);
}

static inline void
ivi_controller_surface_set_opacity(struct ivi_controller_surface *ivi_controller_surface, wl_fixed_t opacity)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SET_OPACITY, opacity);
}

static inline void
ivi_controller_surface_set_source_rectangle(struct ivi_controller_surface *ivi_controller_surface, int32_t x, int32_t y, int32_t width, int32_t height)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SET_SOURCE_RECTANGLE, x, y, width, height);
}

static inline void
ivi_controller_surface_set_destination_rectangle(struct ivi_controller_surface *ivi_controller_surface, int32_t x, int32_t y, int32_t width, int32_t height)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SET_DESTINATION_RECTANGLE, x, y, width, height);
}

static inline void
ivi_controller_surface_set_configuration(struct ivi_controller_surface *ivi_controller_surface, int32_t width, int32_t height)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SET_CONFIGURATION, width, height);
}

static inline void
ivi_controller_surface_set_orientation(struct ivi_controller_surface *ivi_controller_surface, int32_t orientation)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SET_ORIENTATION, orientation);
}

static inline void
ivi_controller_surface_screenshot(struct ivi_controller_surface *ivi_controller_surface, const char *output)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SCREENSHOT, output);
}

static inline void
ivi_controller_surface_send_stats(struct ivi_controller_surface *ivi_controller_surface)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_SEND_STATS);
}

static inline void
ivi_controller_surface_destroy(struct ivi_controller_surface *ivi_controller_surface, int32_t id)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_surface,
			 IVI_CONTROLLER_SURFACE_DESTROY, id);
}

#define IVI_CONTROLLER_SCREEN_DESTROY	0
#define IVI_CONTROLLER_SCREEN_CLEAR	1
#define IVI_CONTROLLER_SCREEN_ADD_LAYER	2
#define IVI_CONTROLLER_SCREEN_SCREENSHOT	3
#define IVI_CONTROLLER_SCREEN_SET_RENDER_ORDER	4

#define IVI_CONTROLLER_SCREEN_DESTROY_SINCE_VERSION	1
#define IVI_CONTROLLER_SCREEN_CLEAR_SINCE_VERSION	1
#define IVI_CONTROLLER_SCREEN_ADD_LAYER_SINCE_VERSION	1
#define IVI_CONTROLLER_SCREEN_SCREENSHOT_SINCE_VERSION	1
#define IVI_CONTROLLER_SCREEN_SET_RENDER_ORDER_SINCE_VERSION	1

static inline void
ivi_controller_screen_set_user_data(struct ivi_controller_screen *ivi_controller_screen, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_controller_screen, user_data);
}

static inline void *
ivi_controller_screen_get_user_data(struct ivi_controller_screen *ivi_controller_screen)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_controller_screen);
}

static inline uint32_t
ivi_controller_screen_get_version(struct ivi_controller_screen *ivi_controller_screen)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_controller_screen);
}

static inline void
ivi_controller_screen_destroy(struct ivi_controller_screen *ivi_controller_screen)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_screen,
			 IVI_CONTROLLER_SCREEN_DESTROY);

	wl_proxy_destroy((struct wl_proxy *) ivi_controller_screen);
}

static inline void
ivi_controller_screen_clear(struct ivi_controller_screen *ivi_controller_screen)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_screen,
			 IVI_CONTROLLER_SCREEN_CLEAR);
}

static inline void
ivi_controller_screen_add_layer(struct ivi_controller_screen *ivi_controller_screen, struct ivi_controller_layer *id_layer)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_screen,
			 IVI_CONTROLLER_SCREEN_ADD_LAYER, id_layer);
}

static inline void
ivi_controller_screen_screenshot(struct ivi_controller_screen *ivi_controller_screen, const char *output)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_screen,
			 IVI_CONTROLLER_SCREEN_SCREENSHOT, output);
}

static inline void
ivi_controller_screen_set_render_order(struct ivi_controller_screen *ivi_controller_screen, struct wl_array *id_layers)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_controller_screen,
			 IVI_CONTROLLER_SCREEN_SET_RENDER_ORDER, id_layers);
}

#define IVI_SHARE_GET_IVI_SHARE_SURFACE	0

#define IVI_SHARE_GET_IVI_SHARE_SURFACE_SINCE_VERSION	1

static inline void
ivi_share_set_user_data(struct ivi_share *ivi_share, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_share, user_data);
}

static inline void *
ivi_share_get_user_data(struct ivi_share *ivi_share)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_share);
}

static inline uint32_t
ivi_share_get_version(struct ivi_share *ivi_share)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_share);
}

static inline void
ivi_share_destroy(struct ivi_share *ivi_share)
{
	wl_proxy_destroy((struct wl_proxy *) ivi_share);
}

static inline struct ivi_share_surface *
ivi_share_get_ivi_share_surface(struct ivi_share *ivi_share, uint32_t id_surface)
{
	struct wl_proxy *id;

	id = wl_proxy_marshal_constructor((struct wl_proxy *) ivi_share,
			 IVI_SHARE_GET_IVI_SHARE_SURFACE, &ivi_share_surface_interface, NULL, id_surface);

	return (struct ivi_share_surface *) id;
}

struct ivi_share_surface_listener {
	/**
	 * damage - (none)
	 * @frame: (none)
	 */
	void (*damage)(void *data,
		       struct ivi_share_surface *ivi_share_surface,
		       uint32_t frame);
	/**
	 * configure - (none)
	 * @width: (none)
	 * @height: (none)
	 * @stride_align: (none)
	 * @pixel_format: (none)
	 * @frame_count: (none)
	 */
	void (*configure)(void *data,
			  struct ivi_share_surface *ivi_share_surface,
			  uint32_t width,
			  uint32_t height,
			  uint32_t stride_align,
			  uint32_t pixel_format,
			  uint32_t frame_count);
	/**
	 * input_capabilities - (none)
	 * @caps: (none)
	 */
	void (*input_capabilities)(void *data,
				   struct ivi_share_surface *ivi_share_surface,
				   uint32_t caps);
	/**
	 * share_surface_state - (none)
	 * @state: (none)
	 */
	void (*share_surface_state)(void *data,
				    struct ivi_share_surface *ivi_share_surface,
				    uint32_t state);
};

static inline int
ivi_share_surface_add_listener(struct ivi_share_surface *ivi_share_surface,
			       const struct ivi_share_surface_listener *listener, void *data)
{
	return wl_proxy_add_listener((struct wl_proxy *) ivi_share_surface,
				     (void (**)(void)) listener, data);
}

#define IVI_SHARE_SURFACE_DESTROY	0
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_DOWN	1
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_UP	2
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_MOTION	3
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_FRAME	4
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_CANCEL	5

#define IVI_SHARE_SURFACE_DESTROY_SINCE_VERSION	1
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_DOWN_SINCE_VERSION	1
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_UP_SINCE_VERSION	1
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_MOTION_SINCE_VERSION	1
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_FRAME_SINCE_VERSION	1
#define IVI_SHARE_SURFACE_REDIRECT_TOUCH_CANCEL_SINCE_VERSION	1

static inline void
ivi_share_surface_set_user_data(struct ivi_share_surface *ivi_share_surface, void *user_data)
{
	wl_proxy_set_user_data((struct wl_proxy *) ivi_share_surface, user_data);
}

static inline void *
ivi_share_surface_get_user_data(struct ivi_share_surface *ivi_share_surface)
{
	return wl_proxy_get_user_data((struct wl_proxy *) ivi_share_surface);
}

static inline uint32_t
ivi_share_surface_get_version(struct ivi_share_surface *ivi_share_surface)
{
	return wl_proxy_get_version((struct wl_proxy *) ivi_share_surface);
}

static inline void
ivi_share_surface_destroy(struct ivi_share_surface *ivi_share_surface)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_share_surface,
			 IVI_SHARE_SURFACE_DESTROY);

	wl_proxy_destroy((struct wl_proxy *) ivi_share_surface);
}

static inline void
ivi_share_surface_redirect_touch_down(struct ivi_share_surface *ivi_share_surface, uint32_t touch_id, int32_t x, wl_fixed_t y, wl_fixed_t arg4)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_share_surface,
			 IVI_SHARE_SURFACE_REDIRECT_TOUCH_DOWN, touch_id, x, y, arg4);
}

static inline void
ivi_share_surface_redirect_touch_up(struct ivi_share_surface *ivi_share_surface, uint32_t touch_id, int32_t arg2)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_share_surface,
			 IVI_SHARE_SURFACE_REDIRECT_TOUCH_UP, touch_id, arg2);
}

static inline void
ivi_share_surface_redirect_touch_motion(struct ivi_share_surface *ivi_share_surface, int32_t x, wl_fixed_t y, wl_fixed_t arg3)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_share_surface,
			 IVI_SHARE_SURFACE_REDIRECT_TOUCH_MOTION, x, y, arg3);
}

static inline void
ivi_share_surface_redirect_touch_frame(struct ivi_share_surface *ivi_share_surface)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_share_surface,
			 IVI_SHARE_SURFACE_REDIRECT_TOUCH_FRAME);
}

static inline void
ivi_share_surface_redirect_touch_cancel(struct ivi_share_surface *ivi_share_surface)
{
	wl_proxy_marshal((struct wl_proxy *) ivi_share_surface,
			 IVI_SHARE_SURFACE_REDIRECT_TOUCH_CANCEL);
}

#ifdef  __cplusplus
}
#endif

#endif
