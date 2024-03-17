from lato import ApplicationModule

my_module = ApplicationModule("my_module")


@my_module.handler("alias_of_foo")
def foo():
    print("called via alias")