import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
import configuration as cfg
from fake_headers import Headers

timeDelay = 1.5
if cfg.isGlitching:
    timeDelay = 4


def getDates():
    todaysDate = datetime.datetime.now().strftime("%m/%d/%Y")
    yesterdaysDate = (datetime.datetime.now() -
                      datetime.timedelta(days=1)).strftime("%m/%d/%Y")
    return todaysDate, yesterdaysDate


def filterCounties(counties):
    for key in list(counties.keys()):
        if key.lower() not in [county.lower() for county in cfg.countiesToSearchFor]:
            counties.pop(key)
    return counties


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
    phrasesToFlagForInViolations = cfg.phrasesToFlagForInViolations
    for keyword in phrasesToFlagForInViolations:
        if re.search(keyword, input_string, re.IGNORECASE):
            return True
    return False


def violationHTMLContainsCertificationViolation(driver):
    for i in range(0, 100):
        try:
            commentElement = driver.find_element(
                By.ID, "MainContent_wucPublicInspectionViolations_rptViolations_pnlComments_" + str(i))
            if certification_needed(commentElement.text):
                return True, commentElement.text
        except:
            return False, ""


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


def saveBusinessInfoToFile(facilityInfo, inspectionDate, county, violationText):
    filename = "certification_violations_" + \
        datetime.datetime.now().strftime("%m-%d-%Y") + ".csv"
    if cfg.haveExcelProductKey:
        pd.set_option('display.max_colwidth', 0)
    try:
        df = pd.read_csv(filename, dtype=str)
        new_row = {'Facility Info': facilityInfo,
                   'Inspection Date': str(inspectionDate),
                   'County': county,
                   'Violation Text': str(violationText)}
        df = df._append(new_row, ignore_index=True)
    except FileNotFoundError:
        data = {'Facility Info': [facilityInfo],
                'Inspection Date': [str(inspectionDate)],
                'County': [county],
                'Violation Text': [str(violationText)]}
        df = pd.DataFrame(data, dtype=str)
    df.to_csv(filename, index=False)


def getBusinessesWithViolationsOnPage(driver, leftOffAtRow=0, county=''):
    gridItems = driver.find_elements(By.CLASS_NAME, "GridItem")
    gridAltItems = driver.find_elements(By.CLASS_NAME, "GridAltItem")
    combinedGridItems = combineAllGridItems(gridItems, gridAltItems)

    if int(leftOffAtRow) >= len(combinedGridItems):
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
                time.sleep(timeDelay)
                containsCertificationViolation, violationtext = violationHTMLContainsCertificationViolation(
                    driver)
                if (containsCertificationViolation):
                    facilityInfoElement = driver.find_element(
                        By.ID, "MainContent_wucPublicInspectionViolations_lblFacilityInformation")
                    inspectionDateElement = driver.find_element(
                        By.ID, "MainContent_wucPublicInspectionViolations_lblHeader")
                    inspectionDateInfo = inspectionDateElement.text
                    inspectionDate = inspectionDateInfo[len(
                        "Inspection Violations: "):]
                    facilityInfo = facilityInfoElement.text
                    saveBusinessInfoToFile(
                        facilityInfo, inspectionDate, county, violationtext)
                closeBtn = driver.find_element(By.ID, "cboxClose")
                closeBtn.click()
                time.sleep(timeDelay)
                getBusinessesWithViolationsOnPage(
                    driver, leftOffAtRow + 1, county)
                break
        leftOffAtRow += 1


def runSearch():
    chrome_options = Options()
    if cfg.runInBackground:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--window-size=1920,1080')
        header = Headers(
            browser="chrome",
            os="win",
            headers=False
        )
        customUserAgent = header.generate()['User-Agent']
        chrome_options.add_argument(f"user-agent={customUserAgent}")
    if cfg.keepBrowserOpenAfterFinished:
        chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.pafoodsafety.pa.gov/Web/Inspection/PublicInspectionSearch.aspx"
    driver.get(url)

    PACounties = filterCounties(getCounties(driver))
    if cfg.startDate == '' or cfg.endDate == '':
        endDate, startDate = getDates()
    else:
        startDate = cfg.startDate
        endDate = cfg.endDate

    for county in dict.items(PACounties):
        clickComplianceCheckbox(driver)
        selectCounty(driver, county[1])
        selectStartDate(driver, startDate)
        selectEndDate(driver, endDate)
        clickSearch(driver)
        numPages = getNumPagesForCounty(driver)
        getBusinessesWithViolationsOnPage(driver, 0, county[0])
        for page in range(1, numPages):
            time.sleep(timeDelay)
            goToNextPage(driver, page)
            time.sleep(timeDelay)
            getBusinessesWithViolationsOnPage(driver, 0, county[0])


if __name__ == "__main__":
    runSearch()
