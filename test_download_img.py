import urllib.request



def download_image(_url, file_path):
    full_path = file_path+'banana.jpg'
    urllib.request.urlretrieve(_url, full_path)

url = input('Enter url to download: ')
path = input('Enter download path: ')
download_image(url, path)
# "https://i1.sndcdn.com/artworks-000353472375-9w5dmg-t3000x3000.jpg"
# 'E:\Jonah B\Music\Unused Artwork\'





########## BELOW IS A FAILED ATTEMPT AT AUTOMATED RIGHT CLICK TO DOWNLOAD #################

#browser = webdriver.Chrome(r"C:\Users\jonah\PycharmProjects\untitled\drivers\chromedriver.exe")
#browser.get("https://i1.sndcdn.com/artworks-000353472375-9w5dmg-t3000x3000.jpg")
#browser.get("http://the-internet.herokuapp.com/key_presses")
#img = browser.find_element_by_xpath("/html/body/img")
#actions = ActionChains(browser)
#actions.context_click(img).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
#time.sleep(1)
#actions.key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()