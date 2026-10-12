from utils.response_schema import BasePaginator



class MartyrPagination(BasePaginator):
    page_size = 12
    message = 'Martyrs Retrieved Successfully'