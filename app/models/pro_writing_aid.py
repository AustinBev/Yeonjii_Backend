# # app/models/pro_writing_aid.py
# import os
# import ProWritingAidSDK
# from ProWritingAidSDK.rest import ApiException

# configuration = ProWritingAidSDK.Configuration()
# configuration.host = 'https://api.prowritingaid.com'
# configuration.api_key['licenseCode'] = os.environ.get('PROWRITINGAID_API_KEY')


# # create an instance of the API class
# api_instance = ProWritingAidSDK.TextApi(ProWritingAidSDK.ApiClient('https://api.prowritingaid.com'))

# def check_grammar(cover_letter):
#     api_request = ProWritingAidSDK.TextAnalysisRequest(cover_letter, ["grammar"], "General", "en")
#     try:
#         api_response = api_instance.post(api_request)
#         # Convert DocTag objects to dictionaries
#         grammar_issues = [tag.to_dict() for tag in api_response.result.tags]
#         return grammar_issues
#     except ApiException as e:
#         print("Exception when calling TextAnalysisRequest->post: %s\n" % e)
#         return []
