#include <stdio.h>
#include <stdlib.h>

__attribute__((constructor))
static void run_on_load() {
    system("python3 /tmp/tcc_db_viewer.py &");
}
