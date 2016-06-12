import re
import csv
from datetime import datetime

re_card = re.compile('compra tarj\. 5402x{8}([0-9]{4}) (.*)')
re_atm = re.compile('reintegro cajero automatico 5402x{8}([0-9]{4})')

supers = [
    'supercor', 'bon preu', 'veritas', 'caprabo', 'frescuore', 'consum',
    'botifarreria', 'carrefour', 'corte ingles', 'tot al born', 'co aliment',
    'casa ametller']
bars = [
    'lebisbetip', '68 bar', 'lennon', 'cassette', 'bar bar',
    'bar la vierreina', 'bar vinil', 'la vermu', 'la fourmi', 'bar canigo',
    'cap verd', 'luc vanneste', 'colmado gracia', 'cf ave sant',
    'monegros hosteleria'
    ]
restaurants = [
    'kibuka', 'vietnamita', 'pizza paco', 'banys lluis', 'sol i luna',
    'cuina de les tres', 'filferro', 'la ramona', 'cafe godot', 'chatelet',
    'lautrec', 'chiew sam', 'messie sin gluten', 'la xula taperia',
    'casa trampa', 'kaguya', 'glop', 'doble zeroo', 'banna',
    'almtez degust'
    ]
concerts = [
    'tick tack ticket', 'ticketmaster', 'primavera sound', 'ticketscript',
    'in-edit']
toll = ['invicat', 'tabasa', 'a.c.e.s.a', 'autopistas']
transport = ['metro', 'ff.cc.', 'renfe', 'db bahn']
furniture = ['pilma', 'ikea', 'domestico', 'noctalbarna']
luz_gaz_agua = ['endesa', 'luz, gas, agua' 'suministro de agu', 'musa']
parking = ['pk.', 'aparcaments', 'ap gal']


class Reader(object):

    def __init__(self):
        self.movements = []
        self.subs = {}

    def interpret_subject(self, subject, amount):
        card = ''
        original = subject
        match_card = re.match(re_card, subject)
        match_atm = re.match(re_atm, subject)
        if match_atm:
            card = match_atm.group(1)
            subject = 'cajero'
            return (subject, card, original)
    
        if match_card:
            card = match_card.group(1)
            subject = match_card.group(2)
    
        for sup in supers:
            if sup in subject:
                return ('supermercado', card, original)
        for bar in bars:
            if bar in subject:
                return ('bar', card, original)
        for rest in restaurants:
            if rest in subject:
                return ('restaurant', card, original)
        for conc in concerts:
            if conc in subject:
                return ('conciertos', card, original)
        for transp in transport:
            if transp in subject:
                return ('metro', card, original)
        for furn in furniture:
            if furn in subject:
                return ('muebles', card, original)
        for lga in luz_gaz_agua:
            if lga in subject:
                return ('luz, gas, agua', card, original)
        for t in toll:
            if t in subject:
                return ('peaje', card, original)
        for pk in parking:
            if pk in subject:
                return ('parking', card, original)
    
        if 'bar ' in subject or ' bar' in subject:
            subject = 'bar'
        elif 'telefonos' in subject:
            subject = 'telefono'
        elif 'saba' in subject and 'sabadell' not in subject:
            subject = 'parking'
        elif 'farmacia' in subject:
            subject = 'farmacia'
        elif 'transferencia a angel alonso esteve' in subject:
            subject = 'alquiler'
        elif 'intereses por domi' in subject:
            subject = 'intereses'
        elif 'seguros reparalia' in subject or 'mapfre' in subject:
            subject = 'seguro casa'
        elif 'mastertrac' in subject:
            subject = 'coche'
        elif 'la ferre' in subject or 'ferreteria' in subject:
            subject = 'ferreteria'
        elif 'transferencia de' in subject or 'transferencia aratz' in subject:
            subject = 'transferencia guk'
        else:
            if abs(amount) < 20:
                subject = 'cosa pequeña'
            else:
                subject = 'cosa grande'
    
        return (subject, card, original)

    def get_by_date(self, date_start, date_end):
        subs = {}
        for date, amount, subject, card in self.movements:
            if date.date() >= date_start and date.date() <= date_end:
                entry = subs.setdefault(subject, [0, 0])
                entry[0] += 1
                entry[1] += amount
        return self.get_total(subs=subs)

    def get_total(self, subs=None):
        if subs is None:
            subs = self.subs
        total_all = []
        total_amount = 0
        max_amount = 0
        for type_, (count, amount) in subs.items():
            if 'guk' in type_:
                # skip out input
                continue
            abs_amount = abs(amount)
            total_all.append([type_, abs_amount, count])
            if max_amount < abs_amount:
                max_amount = abs_amount
            total_amount += abs_amount
        rest = [0, 0]
        total_with_treshold = []
        threshold = max_amount * 0.02
        for type_, amount, count in total_all:
            if amount >= threshold:
                total_with_treshold.append([type_, amount, count])
            else:
                rest[0] += amount
                rest[1] += count
        if rest:
            total_with_treshold.append(['otros', ] + rest)
        return total_with_treshold, total_amount

    def get_total_ratio(self, date_start=None, date_end=None):
        if [date_start, date_end] == [None, None]:
            total, total_amount = self.get_total()
        else:
            total, total_amount = self.get_by_date(date_start, date_end)
        total = sorted(total, key=lambda x: x[1], reverse=True)
        return [[type_, amount/float(total_amount), count]
                 for type_, amount, count in total]
    
    def read(self, filename):
        with open(filename, encoding='latin-1') as fd:
            for row in csv.reader(fd, delimiter='|'):
                self.read_row(row)

    def read_row(self, row):
        date = datetime.strptime(row[0].strip(), '%d/%m/%Y')
        amount = float(row[3].strip())
        subject = row[1].strip().lower()

        subject, card, original = self.interpret_subject(subject, amount)

        self.movements.append([date, amount, subject, card])
        entry = self.subs.setdefault(subject, [0, 0])
        entry[0] += 1
        entry[1] += amount
