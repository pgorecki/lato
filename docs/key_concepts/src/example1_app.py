from lato import Application
from example1_module import my_module

app = Application("alias_example")
app.include_submodule(my_module)


app.call("alias_of_foo")