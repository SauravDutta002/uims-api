const fs = require('fs');
const { login } = require('./server/cuims/scraper');

async function test() {
  console.log('Logging in...');
  const session = await login('24BCS10029', 'Skill1000@');
  console.log('Fetching timetable...');
  const resp = await session.get('https://students.cuchd.in/frmMyTimeTable.aspx');
  
  fs.writeFileSync('timetable_page.html', resp.data);
  console.log('Saved to timetable_page.html');
  
  // also try to do the postback
  const cheerio = require('cheerio');
  const $ = cheerio.load(resp.data);
  const vs = $('input[name="__VIEWSTATE"]').val();
  
  if (vs) {
    const formData = {
      __VIEWSTATE: vs,
      __EVENTTARGET: 'ctl00$ContentPlaceHolder1$ReportViewer1$ctl09$Reserved_AsyncLoadTarget',
    };
    const resp2 = await session.postForm('https://students.cuchd.in/frmMyTimeTable.aspx', formData);
    fs.writeFileSync('timetable_postback.html', resp2.data);
    console.log('Saved postback to timetable_postback.html');
  }
}

test().catch(console.error);
