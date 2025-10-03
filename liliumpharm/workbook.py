import xlsxwriter
from django.http import HttpResponse


class Workbook(xlsxwriter.Workbook):
    def __init__(self, filename) -> None:
        # Creating a Response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response[
            "Content-Disposition"
        ] = f"attachment; filename={filename}.xlsx"

        self.response = response

        # Preparing Formats
        # self.DATE_FORMAT = self.add_format({'num_format': 'mmmm d yyyy', 'border': 1})
        # self.CELLS_FORMAT = self.add_format({
        #     'border': 1,
        # })

        super(Workbook, self).__init__(response, {'in_memory': True})

    def worksheet(self, title, label):
        # Creating Worksheet
        worksheet = self.add_worksheet(label)

        # Writing Document Header
        worksheet.set_column('A:B', 15)
        worksheet.merge_range('A3:B3', '')
        worksheet.insert_image('A3', 'static/img/logo.png', {'x_scale': 0.3, 'y_scale': 0.3})

        merge_format = self.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap':'true'})
        worksheet.set_column('C:E', 30)

        document_header_title = '''
            Nom et prénom du gérant : NAWAFLEH MOHAMED
            Nom et prénom ou raison sociale : LILIUM PHARMA ALGERIE
            Statut juridique : EURL
            Capital social : 140 000,00 DA
        ''' 
        
        worksheet.merge_range('C3:E3', document_header_title, merge_format)
        worksheet.set_row(2, 90)

        
        document_title = title.upper()

        worksheet.merge_range('C5:E6', document_title, merge_format)
        worksheet.set_row(4, 30)

        return worksheet
