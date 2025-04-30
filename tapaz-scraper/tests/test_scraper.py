import pytest
from src.scraper import scrape_new_window, azetoengdate

def test_azetoengdate():
    assert azetoengdate("Bugün") == datetime.today().strftime('%m %d')
    assert azetoengdate("Dünən") == (datetime.today() - timedelta(days=1)).strftime('%m %d')
    assert azetoengdate("15 yanvar") == "01 15"
    assert azetoengdate("28 fevral") == "02 28"
    assert azetoengdate("10 mart") == "03 10"
    assert azetoengdate("25 aprel") == "04 25"
    assert azetoengdate("5 may") == "05 05"
    assert azetoengdate("12 iyun") == "06 12"
    assert azetoengdate("20 iyul") == "07 20"
    assert azetoengdate("30 avqust") == "08 30"
    assert azetoengdate("15 sentyabr") == "09 15"
    assert azetoengdate("10 oktyabr") == "10 10"
    assert azetoengdate("25 noyabr") == "11 25"
    assert azetoengdate("1 dekabr") == "12 01"

def test_scrape_new_window(mocker):
    mock_driver = mocker.patch('src.scraper.driver')
    mock_driver.find_element.return_value.text = "Test Product"
    mock_driver.find_elements.return_value = [mock_driver.find_element.return_value]
    
    dic = {
        "full_name": [],
        "location": [],
        "comp_name": [],
        "price": [],
        "currency": [],
        "date": [],
        "description": [],
        "type": []
    }
    
    result = scrape_new_window("http://test-url.com", dic)
    
    assert len(result["full_name"]) == 1
    assert result["full_name"][0] == "Test Product"