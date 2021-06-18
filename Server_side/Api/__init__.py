import Api.test as api_test
import Api.save_image as api_save_image
import Api.get_image_info as api_get_image_info
import Api.get_keyword_user as api_get_keyword_user
import Api.get_userdata as api_get_userdata
import Api.get_all_keyword as api_get_all_keyword

class Frontend_api():
    def __init__(self, dist) -> None:
        self.dist = dist
        
    def strategy_executer(self, strategy, request_data):
        return {
            'test': lambda: api_test.main(self.dist, request_data),
            'save_image': lambda: api_save_image.main(self.dist, request_data),
            'get_image_info': lambda: api_get_image_info.main(self.dist, request_data),
            'get_keyword_user': lambda: api_get_keyword_user.main(self.dist, request_data),
            'get_userdata': lambda: api_get_userdata.main(self.dist, request_data),
            'get_all_keyword': lambda: api_get_all_keyword.main(self.dist, request_data),
        }[strategy]()

