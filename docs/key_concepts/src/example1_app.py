from example1_module import my_module

from lato import Application

app = Application("alias_example")
app.include_submodule(my_module)


app.call("alias_of_foo")
