import re, requests, time, os, json


def get_k_parameter_re_captcha_v2(driver) -> str:
    print("get_k_parameter_re_captcha_v2")

    iframe_with_k_parameter = driver.find_element_by_xpath(
        '//*[@id="exportData-reCAPTCHA"]/div/div/div/div/iframe'
    )
    src_attribute = iframe_with_k_parameter.get_attribute("src")
    regex_pattern = "((k=).+?(?=&))"
    k_parameter = re.search(regex_pattern, src_attribute).group()[2:]

    return k_parameter


def re_captcha_v2_post(driver, k_parameter) -> str:
    print("re_captcha_v2_post")

    post_api_endpoint = "http://2captcha.com/in.php"

    api_key = os.getenv("CAPTCHA_API_KEY")
    post_method = "userrecaptcha"
    post_google_key = k_parameter
    post_page_url = driver.current_url

    post_api_params = {
        "key": api_key,
        "method": post_method,
        "googlekey": post_google_key,
        "pageurl": post_page_url,
    }

    id_re_captcha_v2 = requests.post(
        url=post_api_endpoint, params=post_api_params, json=1
    ).text[3:]
    time.sleep(20)

    return id_re_captcha_v2


def re_captcha_v2_get(driver, captcha_id) -> None:
    print("re_captcha_v2_get")

    get_api_endpoint = "http://2captcha.com/res.php"

    api_key = os.getenv("CAPTCHA_API_KEY")
    get_action = "get"
    get_id = captcha_id

    get_api_params = {"key": api_key, "action": get_action, "id": get_id}

    answer_token = requests.get(url=get_api_endpoint, params=get_api_params).text

    recount = 1
    wait_time = 10

    while answer_token == "CAPCHA_NOT_READY":
        print(
            f"CAPCHA_NOT_READY for the {recount} time and will wait {wait_time} seconds now"
        )

        time.sleep(wait_time)

        recount += 1

        answer_token = requests.get(url=get_api_endpoint, params=get_api_params).text

    print("answer token received")
    answer_token = answer_token[3:]

    return answer_token


def captcha_request_one(driver, bearer_token, answer_token) -> None:
    print("captcha_request_one")

    id_for_post = driver.current_url
    id_for_post = id_for_post.split("/patient")[1]
    id_for_post = id_for_post.split("/profile")[0]
    id_for_post = id_for_post.split("/")[1]

    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "NEWYU-LV-Web-Version": "3.5.25",
        "sec-ch-ua-mobile": "?0",
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Origin": "https://www.libreview.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": driver.current_url,
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
    }

    data = json.dumps(
        {
            "captchaResponse": f"{answer_token}",
            "type": "glucose",
        }
    )

    response = requests.post(
        f"https://api-us.libreview.io/patients/{id_for_post}/export",
        headers=headers,
        data=data,
    )

    response = json.loads(response.text)
    second_bearer_token = response["ticket"]["token"]
    second_request_url = response["data"]["url"]

    return [second_bearer_token, second_request_url]


def captcha_request_two(driver, second_bearer_token, second_request_url):
    print("captcha_request_two")

    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "NEWYU-LV-Web-Version": "3.5.25",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {second_bearer_token}",
        "Origin": "https://www.libreview.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": driver.current_url,
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
    }

    response = requests.get(
        second_request_url,
        headers=headers,
    )

    response = json.loads(response.text)
    client_for_third_request = response["data"]["lp"].split("?client")[1][1:]
    endpoint_for_third_request = response["data"]["lp"].split("?client")[0]

    return [client_for_third_request, endpoint_for_third_request]


def captcha_request_three(driver, request_client, endpoint_for_third_request):
    print("captcha_request_three")

    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Accept": "application/json, text/plain, */*",
        "NEWYU-LV-Web-Version": "3.5.25",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "Origin": "https://www.libreview.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": driver.current_url,
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
    }

    params = (("client", request_client),)

    response = requests.get(
        endpoint_for_third_request,
        headers=headers,
        params=params,
    )

    response_for_fourth_request = json.loads(response.text)
    endpoint_for_fourth_request = response_for_fourth_request["args"]["url"]

    return endpoint_for_fourth_request


def captcha_request_four(driver, endpoint_for_fourth_request):
    print("captcha_request_four")

    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Origin": "https://www.libreview.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": driver.current_url,
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
    }

    response = requests.get(
        endpoint_for_fourth_request,
        headers=headers,
    )

    glucose_data = response.content.decode("utf-8")

    return glucose_data


def write_glucose_data_to_file(glucose_data):
    print("write_glucose_data_to_file")

    with open("data.csv", "a") as file:
        file.write(glucose_data)