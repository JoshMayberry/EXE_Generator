major = 0
minor = 0
micro = 1
suffix = "a"
releaselevel = {"a": "alpha", "b": "beta", None: "final"}.get(suffix, "candidate")
serial = 0

version_info = (major, minor, micro, releaselevel, serial)

if (suffix is None):
    version = "{}.{}.{}".format(major, minor, micro)
else:
    version = "{}.{}.{}{}".format(major, minor, micro, suffix)
