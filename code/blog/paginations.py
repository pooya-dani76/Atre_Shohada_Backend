from utils.response_schema import BasePaginator

class BlogPagination(BasePaginator):
    page_size = 10 
    message = "Blogs Retrieved Successfully"