from conans import ConanFile, CMake
import os

channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "hoxnox")

class OpenSSLTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "openssl/1.1.0e@%s/%s" % (username, channel)
    #default_options = "openssl:system=True", "openssl:root=/tmp/sss", "openssl:shared=true"
    default_options = "openssl:shared=True"
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll"   , dst="bin", src="bin")
        self.copy(pattern="*.dylib*", dst="bin", src="lib")
        self.copy(pattern="*.so*"   , dst="lib", src="lib")

    def test(self):
        os.chdir("bin")
        self.run(".%stest" % os.sep)
