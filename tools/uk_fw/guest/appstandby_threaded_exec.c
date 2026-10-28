/* VM-only ELF launcher selecting the threaded Qt render loop for AppStandbyClock. */
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    (void)argc;
    if (setenv("QSG_RENDER_LOOP", "threaded", 1) != 0)
        return 111;
    argv[0] = (char *)"/AppStandbyClock.real";
    execv(argv[0], argv);
    return 112;
}
