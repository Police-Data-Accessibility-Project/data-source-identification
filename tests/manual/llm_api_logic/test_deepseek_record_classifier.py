import pytest

from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.deepseek import DeepSeekRecordClassifier


@pytest.mark.asyncio
async def test_deepseek_record_classifier():
    from src.db.models.impl.url.html.content.enums import HTMLContentType as hct

    d = {
        hct.TITLE: "Oath of Office for Newly Promoted Corporal Lumpkin with Acworth Police – City of Acworth, GA",
        hct.DESCRIPTION: "At the Thursday, November 2 regular city council meeting, Chief Evans administered the oath of office and swearing in of Corporal Cody Lumpkin. Corporal Lumpkin was surrounded by his family and members of the Acworth Police Department for the occasion. Corporal Lumpkin began employment with the Acworth Police Department on June 8,",
        hct.H3: ["Oath of Office for Newly Promoted Corporal Lumpkin with Acworth Police"],
        hct.H4: ["Share this on Social Media"],
        hct.DIV: "PHONE DIRECTORY RESOURCES Search for: Search Button NEWS DEPARTMENTS GOVERNANCE & DEVELOPMENT Administration Development Clerks Office Court Services DDA, Tourism, and Historic Preservation OPERATIONS Parks, Recreation, and Community Resources Power, Public Works, and Stormwater SUPPORT SERVICES Customer Service Human Resources Finance Information Technology PUBLIC SAFETY Acworth Police RESIDENTS Public Art Master Plan Application for Boards & Commissions Board of Aldermen Customer Service Parks, Recreation, and Community Resources Historic Acworth Master Fee Schedule E-News Sign Up Online Payments BUSINESS Bids & Projects E-Verify Permits, Applications, & Ordinances City Code of Ordinances Master Fee Schedule Start a Business EVENTS VISIT ACWORTH NEWS DEPARTMENTS GOVERNANCE & DEVELOPMENT Administration Development Clerks Office Court Services DDA, Tourism, and Historic Preservation OPERATIONS Parks, Recreation, and Community Resources Power, Public Works, and Stormwater SUPPORT SERVICES Customer Service Human Resources Finance Information Technology PUBLIC SAFETY Acworth Police RESIDENTS Public Art Master Plan Application for Boards & Commissions Board of Aldermen Customer Service Parks, Recreation, and Community Resources Historic Acworth Master Fee Schedule E-News Sign Up Online Payments BUSINESS Bids & Projects E-Verify Permits, Applications, & Ordinances City Code of Ordinances Master Fee Schedule Start a Business EVENTS VISIT ACWORTH Oath of Office for Newly Promoted Corporal Lumpkin with Acworth Police Published On: November 3, 2023 At the Thursday, November 2 regular city council meeting, Chief Evans administered the oath of office and swearing in of Corporal Cody Lumpkin.  Corporal Lumpkin was surrounded by his family and members of the Acworth Police Department for the occasion.  Corporal Lumpkin began employment with the Acworth Police Department on June 8 , 2015, and has served as a patrol officer in addition to time spent time in Special Operations prior to his recent promotion. Share this on Social Media 4415 Center Street, Acworth GA 30101 Phone Directory Contact Us © 2025 City of Acworth Acworth is located in the foothills of the North Georgia mountains and is nestled along the banks of Lake Acworth and Lake Allatoona, hence its nickname “The Lake City.” The city boasts a rich history, a charming downtown, abundant outdoor recreational activities, a vibrant restaurant scene, and an active festival and events calendar. Acworth is one of the best, family-friendly destinations in the Atlanta region. Come discover why You’re Welcome in Acworth! ESS | Webmail | Handbook | Peak | Laserfiche | Login ",
    }
    content_infos = []
    for content_type, value in d.items():
        content_info = URLHTMLContentInfo(content_type=content_type, content=value)
        content_infos.append(content_info)

    classifier = DeepSeekRecordClassifier()
    result = await classifier.classify_url(content_infos)
    print(result)