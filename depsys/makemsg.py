#!/usr/bin/env python
# -*- coding: utf-8 -*-

from depsys.models import Record, Project
import datetime, pdfkit, os, pathlib
import setting

# create pdf report in temp_path here
temp_path = setting.temp_path


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
        html_head = """\
        <html>\
        <head>\
        <meta charset="UTF-8">\
        </head>\
            <h1>最近""" + str(len(records_list)) + """天发布记录</h1>\
            """
        html_tables = ""
        for records in records_list:
            if records['num'] == 0:
                html_table = """\
                <p>""" + records['date'] + """</p>\
                <p>----无发布记录。----</p>\
                """
            else:
                html_table = """
                <p>""" + records['date'] + """<p>\
                <TABLE BORDER=1>\
                    <TR>\
                        <TH>当日发布工程数</TH>\
                    </TR>\
                    <TR>\
                        <TD>""" + str(records['num']) + """</TD>\
                    </TR>\
                </TABLE>\
                <TABLE BORDER=1>\
                    <TR>\
                        <TH>发布日期</TH>\
                        <TH>发起人</TH>\
                        <TH>工程</TH>\
                        <TH>发布原因</TH>\
                    </TR>\
                """
                for record in records['records']:
                    project = Project.query.filter_by(project_id=record.project_id).first()
                    project_name = project.project_name
                    html_table = html_table + """\
                    <TR>\
                        <TD>""" + str(record.time_begin) + """</TD>\
                        <TD>""" + record.requester + """</TD>\
                        <TD>""" + project_name + """</TD>\
                        <TD>""" + record.deploy_reason + """</TD>\
                    </TR>\
                    """
                html_table = html_table + """\
                </TABLE>\
                """
            html_tables = html_tables + html_table
        html = html_head + html_tables + """</html>"""

        return html

    def make_pdf(self, srcfile, filename):
        """Convert html string to pdf file"""
        # get and cd current path
        root = os.path.dirname(os.path.realpath(__file__))
        root = pathlib.Path(root)
        os.chdir(str(root))
        # mkdir temp path
        exists = os.path.exists(temp_path)
        if not exists:
            os.makedirs(temp_path)

        html = srcfile
        pdf_file = root.joinpath(temp_path, filename)
        try:
            pdfkit.from_string(html, pdf_file)
        except Exception as Err:
            return ("Failed to convert pdf file duo to: ", str(Err))
        else:
            return pdf_file
