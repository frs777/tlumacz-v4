#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int join_path(char *dst, size_t capacity, const char *root, const char *suffix) {
    size_t root_len = strlen(root);
    size_t suffix_len = strlen(suffix);
    if (root_len + suffix_len + 1 > capacity) return -1;
    memcpy(dst, root, root_len);
    memcpy(dst + root_len, suffix, suffix_len + 1);
    return 0;
}

int main(int argc, char **argv) {
    char self[PATH_MAX];
    char root[PATH_MAX];
    char bash[PATH_MAX];
    char script[PATH_MAX];

    ssize_t n = readlink("/proc/self/exe", self, sizeof(self) - 1);
    if (n <= 0 || n >= (ssize_t)sizeof(self) - 1) {
        perror("readlink /proc/self/exe");
        return 127;
    }
    self[n] = '\0';

    char *bin = strrchr(self, '/');
    if (!bin) return 127;
    *bin = '\0';
    char *parent = strrchr(self, '/');
    if (!parent) return 127;
    *parent = '\0';
    if (strlen(self) + 1 > sizeof(root)) return 127;
    memcpy(root, self, strlen(self) + 1);
    if (join_path(bash, sizeof(bash), root, "/bin/bash") != 0) return 127;
    if (join_path(script, sizeof(script), root, "/libexec/apertium-real") != 0) return 127;

    char path_env[PATH_MAX];
    if (join_path(path_env, sizeof(path_env), root, "/bin") != 0) return 127;
    setenv("APERTIUM_PATH", path_env, 1);
    setenv("PATH", path_env, 1);

    for (int i = 1; i + 1 < argc; ++i) {
        if (strcmp(argv[i], "-d") == 0) {
            if (chdir(argv[i + 1]) != 0) {
                perror("chdir Apertium data dir");
                return 127;
            }
            break;
        }
    }

    char **child = calloc((size_t)argc + 2, sizeof(char *));
    if (!child) return 127;
    child[0] = bash;
    child[1] = script;
    for (int i = 1; i < argc; ++i) child[i + 1] = argv[i];
    child[argc + 1] = NULL;

    execv(bash, child);
    perror("exec private Apertium shell");
    free(child);
    return 127;
}
