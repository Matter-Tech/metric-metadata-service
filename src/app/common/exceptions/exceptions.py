from matter_exceptions import DetailedException


class HelloResponseNotFoundError(DetailedException):
    TOPIC = "Hello Response Not Found Error"


class HelloResponseNotSavedError(DetailedException):
    TOPIC = "Hello Response Not Saved Error"
