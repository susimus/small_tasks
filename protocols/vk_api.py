from requests import get as requests_get
from time import sleep as time_sleep


def url_get_friends(input_user_id):
    return (
        "https://api.vk.com/method/friends.get"
        f"?user_id={input_user_id}"  
        "&access_token=bd9f6166bd9f6166bd9f61663cbdf5d4a7bbd9fbd9f6166e17a2cc62ae2f8ecafbc5124"
        "&v=5.52")


def url_get_user_info(input_user_id):
    return (
        "https://api.vk.com/method/users.get"
        f"?user_ids={input_user_id}"
        "&fields=contacts"
        "&access_token=bd9f6166bd9f6166bd9f61663cbdf5d4a7bbd9fbd9f6166e17a2cc62ae2f8ecafbc5124"
        "&v=5.52")


while True:
    user_name = input()

    answer_user_id = requests_get(url_get_user_info(user_name)).json()
    if "error" in answer_user_id:
        print("Some error occurred:\n" + answer_user_id["error"]["error_msg"])
        continue
    user_id = answer_user_id['response'][0]['id']

    answer_user_friends = requests_get(url_get_friends(user_id)).json()
    if "error" in answer_user_friends:
        print("Some error occurred:\n" + answer_user_friends["error"]["error_msg"])
        continue
    user_friends = answer_user_friends['response']['items']

    counter = 0
    for user_friend in user_friends:
        counter = (counter + 1) % 45
        if counter == 0:
            time_sleep(1)

        answer_friend_info = requests_get(url_get_user_info(user_friend)).json()
        if 'error' in answer_friend_info:
            print('Error while asking api')
            continue
        answer_friend_info = answer_friend_info['response'][0]

        print(
            str(user_friend)
            + '('
            + answer_friend_info['first_name']
            + ' '
            + answer_friend_info['last_name']
            + '): ',
            end='')

        there_is_some_phone_number = (
            'mobile_phone' in answer_friend_info
            and answer_friend_info['mobile_phone'] != ''
            or (
                'home_phone' in answer_friend_info
                and answer_friend_info['home_phone'] != ''))
        if not there_is_some_phone_number:
            print('no contacts')
            continue
        print()
        if 'mobile_phone' in answer_friend_info and answer_friend_info['mobile_phone'] != '':
            print('\tmobile_phone: ' + str(answer_friend_info['mobile_phone']))
        if 'home_phone' in answer_friend_info and answer_friend_info['home_phone'] != '':
            print('\thome_phone: ' + str(answer_friend_info['home_phone']))

    print('Done')
