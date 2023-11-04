import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re


def getDates():
    todaysDate = datetime.datetime.now().strftime("%m/%d/%Y")
    yesterdaysDate = (datetime.datetime.now() -
                      datetime.timedelta(days=10)).strftime("%m/%d/%Y")
    return todaysDate, yesterdaysDate


def filterCounties(counties):
    counties.pop("UNKNOWN", None)


def getCounties(driver):
    dropdown_element = driver.find_element(By.ID,
                                           'MainContent_wucStateCountiesFS_ddlCounty')
    select = Select(dropdown_element)
    counties = {}
    for option in select.options:
        counties[option.text] = option.get_attribute("value")
    filterCounties(counties)
    return counties


def clickComplianceCheckbox(driver):
    compliance_checkbox = driver.find_element(
        By.ID, "MainContent_chkInCompliance")
    compliance_checkbox.click()


def selectCounty(driver, countyValue):
    dropdown_element = driver.find_element(By.ID,
                                           'MainContent_wucStateCountiesFS_ddlCounty')
    select = Select(dropdown_element)
    select.select_by_value(str(countyValue))


def selectStartDate(driver, dateString):
    date_input = driver.find_element(By.ID,
                                     'MainContent_dteInspectionBeginDate_txtDate')
    date_input.clear()
    new_date = dateString
    date_input.send_keys(new_date)
    date_input.send_keys(Keys.RETURN)


def selectEndDate(driver, dateString):
    date_input = driver.find_element(By.ID,
                                     'MainContent_dteInspectionEndDate_txtDate')
    date_input.clear()
    new_date = dateString
    date_input.send_keys(new_date)
    date_input.send_keys(Keys.RETURN)


def clickSearch(driver):
    search_button = driver.find_element(By.ID, "MainContent_btnSearch")
    search_button.click()


def getNumPagesForCounty(driver):
    try:
        gridPager = driver.find_element(By.CLASS_NAME, "GridPager")
        gridPagerTable = gridPager.find_element(By.TAG_NAME, "table")
        return len(gridPagerTable.find_elements(By.TAG_NAME, "td"))
    except:
        return 1


def goToNextPage(driver, pageNum):
    gridPager = driver.find_element(By.CLASS_NAME, "GridPager")
    gridPagerTable = gridPager.find_element(By.TAG_NAME, "table")
    tdElements = gridPagerTable.find_elements(By.TAG_NAME, "td")
    tdElements[pageNum].click()


def certification_needed(input_string):
    certification_keywords = [
        r"certified food employee",
        r"certified food manager certificate",
        r"certified food manager",
        r"certification is not posted",
        r"food employee certification",
        r"food facility has lost its certified food employee",
        r"food facility does not employ a certified food employee",
        r"food facility does not have an employee with Chester County Certified Food Manager certification",
        r"food facility does not yet employ a certified",
        r"food facility does not yet have an employee with Chester County Certified Food Manager certification",
        r"food facility lost its certified employee",
        r"food facility lost its certified food employee",
        r"food facility lost its certified food manager",
        r"food facility has an employee who held a Certified Food Manager certificate",
        r"food facility has an employee that has taken food safety training program",
        r"food facility has an employee who held a Certified Food Manager certificate",
        r"food facility does not yet employ a certified food employee",
        r"no certified employee",
        r"no certified employee, no certificate",
        r"certified supervisory employee",
        r"supervisory employee certification",
        r"get this certification"
    ]

    for keyword in certification_keywords:
        if re.search(keyword, input_string, re.IGNORECASE):
            return True
    return False


def violationHTMLContainsCertificationViolation(driver):
    for i in range(0, 100):
        try:
            commentElement = driver.find_element(
                By.ID, "MainContent_wucPublicInspectionViolations_rptViolations_pnlComments_" + str(i))
            if certification_needed(commentElement.text):
                return True
        except:
            return False


def combineAllGridItems(gridItems, gridAltItems):
    combinedList = []
    for i in range(0, min(len(gridItems), len(gridAltItems))):
        combinedList.append(gridItems[i])
        combinedList.append(gridAltItems[i])
    if len(gridItems) > len(gridAltItems):
        combinedList += gridItems[len(gridAltItems):]
    elif len(gridAltItems) > len(gridItems):
        combinedList += gridAltItems[len(gridItems):]
    return combinedList


def getBusinessesWithViolationsOnPage(driver, leftOffAtRow=0):
    gridItems = driver.find_elements(By.CLASS_NAME, "GridItem")
    gridAltItems = driver.find_elements(By.CLASS_NAME, "GridAltItem")
    combinedGridItems = combineAllGridItems(gridItems, gridAltItems)

    if leftOffAtRow >= len(combinedGridItems):
        return

    for gridItem in combinedGridItems[leftOffAtRow:]:
        try:
            tdElements = gridItem.find_elements(By.TAG_NAME, "td")
        except:
            return

        for i in range(0, len(tdElements)):
            if i == 5 and "Violation" in tdElements[i].text:
                violationPanelButton = tdElements[i].find_element(
                    By.TAG_NAME, "a")
                violationPanelButton.click()
                time.sleep(1)
                if (violationHTMLContainsCertificationViolation(driver)):
                    print("Found a violation!")
                    driver.save_screenshot(
                        "violation" + str(leftOffAtRow) + ".png")
                closeBtn = driver.find_element(By.ID, "cboxClose")
                closeBtn.click()
                time.sleep(1)
                getBusinessesWithViolationsOnPage(driver, leftOffAtRow + 1)
                break
        leftOffAtRow += 1


def runSearch():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.pafoodsafety.pa.gov/Web/Inspection/PublicInspectionSearch.aspx"
    driver.get(url)

    PACounties = getCounties(driver)
    todaysDate, yesterdaysDate = getDates()

    # for each county
    # for county in dict.items(PACounties):
    clickComplianceCheckbox(driver)
    selectCounty(driver, 1)
    selectStartDate(driver, '10/01/2023')
    selectEndDate(driver, '11/30/2023')
    clickSearch(driver)
    numPages = getNumPagesForCounty(driver)
    getBusinessesWithViolationsOnPage(driver)
    for page in range(1, numPages):
        time.sleep(1)
        goToNextPage(driver, page)
        time.sleep(1)
        getBusinessesWithViolationsOnPage(driver)


if __name__ == "__main__":
    runSearch()
