*** Settings ***
Library    ../resources/ApiExecutionLibrary.py

*** Variables ***
${RESULTS_FILE}    ${EMPTY}
${PAYLOAD_FILE}    ${EMPTY}
${BASE_URL}        ${EMPTY}
${DEFAULT_AUTH_TYPE}    ${EMPTY}
${DEFAULT_AUTH_VALUE}    ${EMPTY}
${DEFAULT_AUTH_HEADER_NAME}    Authorization
${DEFAULT_TIMEOUT_SECONDS}    30

*** Keywords ***
Prepare Run Output
    Initialize Run Output    ${RESULTS_FILE}    ${PAYLOAD_FILE}    ${BASE_URL}    ${DEFAULT_AUTH_TYPE}    ${DEFAULT_AUTH_VALUE}    ${DEFAULT_AUTH_HEADER_NAME}    ${DEFAULT_TIMEOUT_SECONDS}
