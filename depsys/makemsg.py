#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Record, Project
import datetime


class Report:
    """Report maker"""
    def get_records(self, date_range):
        """Get report content"""
        now = datetime.datetime.now()
        records_list = []
        for i in range(date_range):
            # get records day by day
            delta = datetime.timedelta(days=(i))
            the_date = now - delta
            range_begin = the_date.strftime('%Y-%m-%d 00:00:00')
            range_end = the_date.strftime('%Y-%m-%d 23:59:59')
            records = Record.query.filter(Record.time_begin.between(range_begin, range_end)).all()
            records_list.append({'num': len(records), 'date': the_date.strftime('%Y-%m-%d'), 'records': records})

        return records_list

    def make_html(self, records_list):
        """Format content to html table"""
        html_head = """
        <meta http-equiv=Content-Type content=text/html; charset=utf-8 />
        <html lang=en>
            <h1>最近""" + len(records_list) + """天发布记录</h1>
        """
        for records in records_list:
            if records['num'] == 0:
                html_table = """
                <p>""" + records['date'] + """</p>
                <p>----无发布记录。----</p>
                """
            else:
                html_table = """
                <p>2018-09-13 Thursday<p>
                <TABLE BORDER=1>
                    <TR>
                        <TH>当日发布工程数</TH>
                    </TR>
                    <TR>
                        <TD>""" + records['num'] + """</TD>
                    </TR>
                </TABLE>
                <TABLE BORDER=1>
                    <TR>
                        <TH>发布日期</TH>
                        <TH>发起人</TH>
                        <TH>工程</TH>
                        <TH>发布原因</TH>
                    </TR>
                """
                for record in records:
                    project = Project.query.filter_by(project_id=record.project_id).first()
                    project_name = project.project_name
                    html_table = html_table + """
                    <TR>
                        <TD>""" + record.time_begin + """</TD>
                        <TD>""" + record.requester + """</TD>
                        <TD>""" + project_name + """</TD>
                        <TD>""" + record.deploy_reason + """</TD>
                    </TR>
                    """
                html_table = html_table + """
                </TABLE>
                """
        html = html_head + html_table + """</html>"""

        return html

    def make_pdf(self):
        pass
