import {test,expect} from '../../apps/web/node_modules/@playwright/test';

test('investigate, inspect evidence with keyboard, graph, and review',async({page})=>{
 await page.goto('/investigate');
 await expect(page.getByRole('heading',{name:'Your company, in context.'})).toBeVisible();
 await expect(page.getByText('196 accessible records',{exact:true})).toBeVisible();
 await page.screenshot({path:`test-results/home-${test.info().project.name}.png`,fullPage:true});
 await page.getByRole('button',{name:'Find launch risks'}).click();
 await expect(page.getByRole('heading',{name:'1 known blocker and an ownership conflict'})).toBeVisible();
 const citation=page.getByRole('button',{name:'Open evidence 1',exact:true}).first();
 await citation.focus();await page.keyboard.press('Enter');
 await expect(page.getByRole('dialog')).toBeVisible();
 await expect(page.locator('blockquote')).not.toBeEmpty();
 await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).not.toBeVisible();
 await page.getByRole('button',{name:'Graph',exact:true}).click();
 await expect(page.locator('.react-flow')).toBeVisible();
 await page.screenshot({path:`test-results/investigation-${test.info().project.name}.png`,fullPage:true});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
 await page.getByRole('button',{name:'Prepare review task'}).click();
 await page.getByRole('button',{name:'Preview review'}).click();
 await expect(page.getByText('Draft · awaiting confirmation')).toBeVisible();
 await page.getByRole('button',{name:'Create review task'}).click();
 await expect(page.getByText('Created',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Close dialog'}).click();
 await page.getByRole('button',{name:'Prepare review task'}).click();
 await page.getByRole('button',{name:'Preview review'}).click();
 await expect(page.getByRole('dialog').getByRole('alert')).toContainText('Rerun');
 await page.getByRole('button',{name:'Close dialog'}).click();
 await page.getByRole('combobox',{name:'Workspace role'}).selectOption('Viewer');
 await expect(page.getByRole('heading',{name:'1 known blocker and an ownership conflict'})).not.toBeVisible();
 await page.getByRole('button',{name:'Find launch risks'}).click();
 await expect(page.getByRole('heading',{name:'More evidence is needed'})).toBeVisible();
 await expect(page.getByText('T-101 blocks Identity Gateway')).not.toBeVisible();
});

test('source browsing, filters and private history',async({page})=>{
 await page.goto('/sources');
 await expect(page.getByRole('heading',{name:'Sources',exact:true})).toBeVisible();
 await page.getByRole('textbox',{name:'Search sources'}).fill('Identity Gateway');
 await expect(page.getByRole('button',{name:'Identity Gateway · operational runbook'})).toBeVisible();
 await page.getByRole('button',{name:'Identity Gateway · operational runbook'}).click();
 await expect(page.getByRole('heading',{name:'Source history'})).toBeVisible();
 await page.keyboard.press('Escape');
 await page.getByRole('combobox',{name:'Workspace role'}).selectOption('Viewer');
 await expect(page.getByRole('button',{name:'Identity Gateway · operational runbook'})).not.toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
});

test('a source revision changes the investigation and explains the removed blocker',async({page})=>{
 await page.goto('/investigate');
 await expect(page.getByRole('combobox',{name:'Workspace role'})).toBeVisible();
 await page.getByRole('combobox',{name:'Workspace role'}).selectOption('Lead');
 await expect(page.getByText('200 accessible records',{exact:true})).toBeVisible();
 const created=page.waitForResponse(r=>r.url().endsWith('/api/v1/investigations')&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Find launch risks'}).click();
 const runId=(await (await created).json()).run_id;
 await expect(page.getByRole('heading',{name:'1 known blocker and an ownership conflict'})).toBeVisible();
 const headers={origin:'http://localhost:3000','x-brain-csrf':'1'};
 try{
  await page.goto('/sources');
  await page.getByRole('button',{name:'Update ticket status',exact:true}).click();
  await page.getByRole('combobox',{name:'Ticket to update'}).selectOption('ticket:T-101');
  await page.getByRole('combobox',{name:'New ticket status'}).selectOption('done');
  await page.getByRole('button',{name:'Save status',exact:true}).click();
  await expect(page.getByRole('status')).toContainText('Indexed');
  await page.goto('/investigate?run='+runId);
  await expect(page.getByText('Sources changed since this answer. Rerun to use current evidence.')).toBeVisible();
  await page.getByRole('button',{name:'Rerun',exact:true}).click();
  await expect(page.getByRole('heading',{name:'No confirmed blockers and an ownership conflict'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'What changed'})).toBeVisible();
  await expect(page.getByText('is no longer an active blocker: updated status is done.',{exact:false})).toBeVisible();
  await page.screenshot({path:`test-results/updated-${test.info().project.name}.png`,fullPage:true});
 }finally{
  const sourceResponse=await page.request.get('/api/v1/sources?limit=100&q=T-101');
  const source=(await sourceResponse.json()).items.find((s:{id:string})=>s.id==='ticket:T-101');
  const envelope={schema_version:'1.0',source_id:'ticket:T-101',kind:'ticket',title:'T-101 · Identity verification check',source_updated_at:'2026-10-17T03:30:00Z',acl_groups:['engineering'],body:'',expected_revision_id:source.active_revision_id,records:{entity_id:'ticket:T-101',status:'blocked',blocks:['service:identity']}};
  const imported=await page.request.post('/api/v1/imports',{headers,multipart:{files:{name:'ticket.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(envelope))}}});
  expect(imported.ok()).toBeTruthy();
  const jobId=(await imported.json()).job_ids[0];
  await expect.poll(async()=> (await (await page.request.get('/api/v1/jobs/'+jobId)).json()).status).toBe('complete');
 }
});


test('a failed saved investigation shows a recoverable error',async({page})=>{
 await page.route('**/api/v1/investigations/run_failed_ui_test',route=>route.fulfill({json:{status:'failed',error:{code:'interrupted',message:'The server restarted. Rerun this investigation.',retryable:true}}}));
 await page.goto('/investigate?run=run_failed_ui_test');
 await expect(page.locator('.errorBanner[role=alert]')).toContainText('Rerun this investigation');
 await expect(page.locator('.answerLayout')).toHaveCount(0);
 await expect(page.getByRole('textbox',{name:'Investigation question'})).toBeVisible();
});

test('workspace handbook opens an editable question and all source pages are searchable',async({page})=>{
 await page.goto('/guide');
 await expect(page.getByRole('heading',{name:'Work with a clearer picture.',exact:true})).toBeVisible();
 await expect(page.getByRole('heading',{name:'Know what each system does'})).toBeVisible();
 await expect(page.getByRole('heading',{name:'Managed Cloud Migration',exact:true})).toBeVisible();
 await expect(page.locator('body')).not.toContainText(/\bdemo\b|\bsynthetic\b|\bfictional\b/i);
 await page.getByRole('textbox',{name:'Search people'}).fill('Maya');
 await expect(page.locator('.peopleDirectory')).toContainText('Maya Rao');
 await expect(page.locator('.directoryPerson')).toHaveCount(1);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
 await page.screenshot({path:`test-results/guide-${test.info().project.name}.png`,fullPage:true});
 await page.getByRole('button',{name:'Try this question'}).first().click();
 await expect(page.getByRole('textbox',{name:'Investigation question'})).toHaveValue('What could block Atlas Client Portal, and which customer commitment is affected?');
 await expect(page.getByRole('combobox',{name:'Investigation entity'}).getByRole('option',{name:'Managed Cloud Migration'})).toHaveCount(1);
 await page.goto('/sources');
 await page.getByRole('textbox',{name:'Search sources'}).fill('T-160');
 await expect(page.locator('.sourceTableCard tbody tr')).toHaveCount(1);
 await expect(page.locator('.sourceTableCard')).toContainText('T-160');
});
