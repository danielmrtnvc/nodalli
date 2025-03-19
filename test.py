from urllib.parse import quote_plus

def build_apollo_search_url(job_titles, location, company_size, industry):
    base_url = "https://app.apollo.io/#/people?page=1&sortByField=recommendations_score&sortAscending=false"
    job_titles_str = "&".join([f"personTitles[]={quote_plus(title)}" for title in job_titles])
    location_str = f"personLocations[]={quote_plus(location)}"
    # Convert company size to Apollo's format (assuming size is a range like "1,10")
    company_size_str = f"organizationNumEmployeesRanges[]={company_size.replace('Micro (', '').replace(' employees)', '')}" 
    industry_str = f"qOrganizationKeywordTags[]={quote_plus(industry)}"
    # Combine all parameters
    search_url = f"{base_url}&{job_titles_str}&{location_str}&{company_size_str}"
    hard_code = "https://app.apollo.io/#/people?page=1&sortByField=recommendations_score&sortAscending=false&personTitles[]=Game%20Developer&personLocations[]=Toronto"
    return search_url
print(build_apollo_search_url(["Game Developer"], "Toronto", "Micro (1-10 employees)", "Technology")) # Expected: "https://app.apollo.io/#/people?page=1&sortByField=recommendations_score&sortAscending=false&personTitles[]=Game%20Developer&personLocations[]=Toronto&organizationNumEmployeesRanges=1-10"

# https://app.apollo.io/#/people?page=1&sortByField=recommendations_score&sortAscending=false&personTitles[]=Game+Developer&personLocations[]=Toronto&organizationNumEmployeesRanges[]=1-10