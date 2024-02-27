Serving the app via FastAPI
===========================

The last step of the tutorial is to demonstrate how `lato` can be integrated with a web framework of your choice. 
For now, let's look at the FastAPI example:

.. code-block:: python

    from fastapi import FastAPI
    from application import Application, create_app
    from queries import GetAllTodos
    
    api = FastAPI()
    api.lato_application = create_app()
    
    async def get_application(request: Request) -> Application:
        """
        Retrieve the application instance from the request.
    
        :param request: The incoming request.
        :return: The Application instance.
        """
        app = request.app.lato_application
        return app
    
    @api.get("/")
    async def root(app: Annotated[Application, Depends(get_application)]):
        result = app.execute(GetAllTodos())
        return {"todos": result}

This concludes the tutorial.