from nxtools import NxConanFile
from conans import tools, AutoToolsBuildEnvironment

# windows is not supported because build process is too complicated
# (perl and nasm required). Use libressl or build by hand and set
# `system` and `root` options

class OpenSSLConan(NxConanFile):
    name = "openssl"
    version = "1.1.0e"
    settings = "os", "compiler", "arch", "build_type"
    url = "http://github.com/hoxnox/conan-openssl"
    license = "https://www.openssl.org/source/license.html"
    description = "OpenSSL is an open source project that provides a robust, commercial-grade, and full-featured " \
                  "toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"
    options = {"shared": [True, False], "with_zlib":[True, False]}
    default_options = "shared=False", "with_zlib=True"

    def config(self):
        if self.options["openssl"].with_zlib:
            self.requires.add("zlib/1.2.11@hoxnox/stable")

    def do_source(self):
        self.retrieve("e703df4eca8b3687af0bec069ea2e7b9fefcb397701dd0d36620fd205cde82a5",
                [
                    "vendor://openssl/openssl/openssl-{v}.tar.gz".format(v=self.version),
                    "https://github.com/openssl/openssl/archive/OpenSSL_{v}.tar.gz".format(v = self.version.replace('.', '_'))
                ],
                "openssl-{v}.tar.gz".format(v=self.version))


    def do_build(self):
        build_dir = "{staging_dir}/src".format(staging_dir=self.staging_dir)
        tools.untargz("openssl-{v}.tar.gz".format(v=self.version), build_dir)
        shared_definition = "no-shared" if not self.options["openssl"].shared else "shared"
        zlib_definition = "no-zlib no-zlib-dynamic" if not self.options["openssl"].with_zlib else \
                "zlib --with-zlib-lib={zlib_pkg_dir}/lib --with-zlib-include={zlib_pkg_dir}/include".format(zlib_pkg_dir = self.deps_cpp_info["zlib"].rootpath)
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            self.run("cd {build_dir}/openssl-OpenSSL_{v} && ./config --prefix=\"{staging}\" {shared} {zlib}".format(
                v = self.version.replace('.', '_'), staging=self.staging_dir, shared=shared_definition,
                build_dir=build_dir, zlib = zlib_definition))
            self.run("cd {build_dir}/openssl-OpenSSL_{v} && make install".format(v = self.version.replace('.', '_'), build_dir = build_dir))


    def do_package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]

