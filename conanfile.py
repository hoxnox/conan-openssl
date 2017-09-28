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
        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11@hoxnox/stable")
            if self.options.shared:
                self.options["zlib"].shared = True

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
        src_dir = "{build_dir}/openssl-OpenSSL_{v}".format(
                v = self.version.replace('.', '_'), build_dir=build_dir)
        shared_definition = "no-shared" if not self.options.shared else "shared"

        zlib_definition = "no-zlib no-zlib-dynamic"
        if self.options.with_zlib:
            if self.options["zlib"].system:
                zlib_definition = "zlib"
            else:
                zlib_definition = "{zlib} --with-zlib-lib={zlib_pkg_dir}/lib --with-zlib-include={zlib_pkg_dir}/include".format(
                        zlib_pkg_dir = self.deps_cpp_info["zlib"].rootpath,
                        zlib = "no-zlib zlib-dynamic" if self.options["zlib"].shared else "zlib no-zlib-dynamic")
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            with tools.chdir(src_dir):
                self.run("./config --prefix=\"{staging}\" {shared} {zlib}".format(
                    staging=self.staging_dir, shared=shared_definition, zlib = zlib_definition))
                self.run("make -j {cpu_count}".format(cpu_count = tools.cpu_count()))
                self.run("make install_sw")


    def do_package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]

