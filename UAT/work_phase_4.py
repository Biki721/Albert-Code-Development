import pandas as pd
import docx

def round_robin(issues, f_emails):
    """Distribute issues among fixers evenly"""
    no_of_fixers = len(f_emails)
    allocation = {f_emails[i]: [] for i in range(no_of_fixers)}
    j = 0
    while issues:
        allocation[f_emails[j]].append(issues[0])
        j = (j + 1) % no_of_fixers
        issues.pop(0)
    return allocation

def getIndexes(dfObj, value):
    """Get index positions of value in dataframe"""
    listOfPos = []
    result = dfObj.isin([value])
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        listOfPos.extend(rows)
    return listOfPos

def get_fixers_by_category(alloc_df, tag, lang, category):
    """Get all available fixers for a specific category"""
    alloc_df['Category'] = alloc_df['Category'].str.strip()
    alloc_tag = alloc_df[alloc_df['Category'] == tag]
    alloc_tag['Module'] = alloc_tag['Module'].str.strip()
    
    if category in list(alloc_tag['Module']):
        alloc_tag = alloc_tag[alloc_tag['Module'] == category]
    if lang in list(alloc_tag['Language']):
        alloc_tag = alloc_tag[alloc_tag['Language'] == lang]
    
    emails = []
    for ele in list(alloc_tag["Fixers Email"]):
        if isinstance(ele, str):
            emails.extend(email.strip() for email in ele.split('\n') if email.strip())
    return emails

def filter_content(report_df, alloc_df, tag, lang, category):
    """Filter and assign content based on criteria"""
    if report_df.empty:
        return {}
    
    issues = list(report_df['Error Link'])
    emails = get_fixers_by_category(alloc_df, tag, lang, category)
    
    if not emails:
        return {}
    return round_robin(issues, emails) if len(emails) > 1 else {emails[0]: issues}

def process_region_domain(df_region, sheet_name, allocationfile, language, cat):
    """Process each region and domain combination"""
    allocation = {}
    if not df_region.empty:
        try:
            alloc_df = pd.read_excel(allocationfile, sheet_name=sheet_name)
            
            # Get categorization based on domain
            if 'Competitor' in sheet_name:
                hybrid = df_region[df_region['Categorization'] == 'CH']
                portalad = df_region[df_region['Categorization'] == 'CP']
            elif 'Marketing' in sheet_name:
                hybrid = df_region[df_region['Categorization'] == 'MH']
                portalad = df_region[df_region['Categorization'] == 'MP']
            else:  # PRP
                hybrid = df_region[df_region['Categorization'] == 'H']
                portalad = df_region[df_region['Categorization'] == 'P']
            
            if not portalad.empty:
                allocation.update(filter_content(portalad, alloc_df, 'Portal Admin', language, cat))
            if not hybrid.empty:
                allocation.update(filter_content(hybrid, alloc_df, 'Hybrid', language, cat))
                
        except Exception as e:
            print(f"Warning: Error processing {sheet_name}: {str(e)}")
    return allocation

def work_alloc_execute(reportfile, allocationfile, arubapath):
    """Main function to execute work allocation"""
    # Read input files
    df_original = pd.read_excel(reportfile)
    language = df_original["Language"][0]
    cat = df_original['Category'][0]
    df = df_original.copy()
    
    # Process URLs and create Error Link column
    df['Error Link'] = df['Error Link'] + "*" + df['Link']
    errors = list(df['Error Link'])
    demo_account = df['Demo Account'].to_list()
    
    # Categorize errors
    categorization = []
    for error in errors:
        error_stripped = str(error.split('*')[0]).strip()
        is_admin = any(k in error_stripped for k in ['notifications', 'tools', 'settings'])
        
        if any(account in demo_account for account in ['demo_competitor@pproap.com', 'demo_mapcompetitor_solp@yopmail.com']):
            error_cat = 'CP' if is_admin else 'CH'
        elif 'marketingpro' in error_stripped:
            error_cat = 'MP' if is_admin else 'MH'
        else:
            error_cat = 'P' if is_admin else 'H'
        categorization.append(error_cat)
    
    df['Categorization'] = categorization
    df_reference = df.copy()
    
    # Process each region
    regions = ['APJ', 'EMEA', 'AMS']
    domains = ['PRP', 'Marketing', 'Competitor']
    allocation = {}
    
    for region in regions:
        df_region = df[df['Region'].isin([region, 'NAR', 'LAR'])]
        for domain in domains:
            sheet_name = f'{domain}_{region}'
            temp_allocation = process_region_domain(df_region, sheet_name, allocationfile, language, cat)
            
            # Merge allocations
            for key in set(list(allocation.keys()) + list(temp_allocation.keys())):
                allocation[key] = allocation.get(key, []) + temp_allocation.get(key, [])
    
    # Handle any unassigned issues
    unassigned_mask = ~df_original['Error Link'].isin([issue for issues in allocation.values() for issue in issues])
    if unassigned_mask.any():
        unassigned_issues = list(df[unassigned_mask]['Error Link'])
        all_fixers = set()
        
        # Collect all available fixers
        for domain in domains:
            for region in regions:
                try:
                    alloc_df = pd.read_excel(allocationfile, sheet_name=f'{domain}_{region}')
                    fixers = get_fixers_by_category(alloc_df, 'Hybrid', language, cat)
                    all_fixers.update(fixers)
                    fixers = get_fixers_by_category(alloc_df, 'Portal Admin', language, cat)
                    all_fixers.update(fixers)
                except Exception:
                    continue
        
        # Assign remaining issues using round-robin
        if all_fixers:
            new_allocation = round_robin(unassigned_issues, list(all_fixers))
            allocation.update(new_allocation)
    
    # Update the original dataframe with assignments
    for email, issues in allocation.items():
        for issue in issues:
            pos = getIndexes(df_reference, issue)
            if pos:
                df_original.loc[pos, "Mail ID"] = email
    
    # Save results
    df_original.to_excel(reportfile, index=None)
    return allocation

def doc_reader(filename):
    """Read content from Word document"""
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText).splitlines()

if __name__ == '__main__':
    
    work_alloc_execute('Reserve\Aggregated Report.xlsx','Fixers_list.xlsx','Aruba Urls\\ArubaAPJ_China_Chinese_T2.txt')