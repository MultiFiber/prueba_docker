import calendar
from datetime import datetime, timedelta

from rest_framework.exceptions import ValidationError
from .models import Technician, Disponibility, Absence, Schedule, schedule_days as days
from rest_framework.response import Response
from OS.models import Os
from operador.models import Operator
from category.models import Category
from direction.models import Direction
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from operator_setting.models import OperatorSetting
from django.db.models import Q

def restar_hora(hora1,hora2):
    formato = "%H:%M:%S"
    if datetime.strptime(hora1, '%H:%M:%S') < datetime.strptime(hora2, '%H:%M:%S'):
        swap = hora2
        hora2 = hora1
        hora1 = swap
    lista = hora2.split(":")
    hora=int(lista[0])
    minuto=int(lista[1])
    segundo=int(lista[2])
    h1 = datetime.strptime(hora1, formato)
    dh = timedelta(hours=hora) 
    dm = timedelta(minutes=minuto)          
    ds = timedelta(seconds=segundo) 
    resultado1 =h1 - ds
    resultado2 = resultado1 - dm
    resultado = resultado2 - dh
    resultado=resultado.strftime(formato)
    return str(resultado)
\


def to_seconds(hora):
    formato = "%H:%M:%S"
    hora = hora.strftime(formato)
    lista = hora.split(":")
    hh=int(lista[0])*3600
    mm=int(lista[1])*60
    ss=int(lista[2])
    suma = hh + mm + ss
    return suma

def dictionary_obj(dictionary,absence_lunch,technician,id,others_absences):
    dictionary['name'] = f"{technician['name']} {technician['last_name']}"
    dictionary['id_technician'] = technician['id']
    dictionary['id_disponibility'] = id
    if absence_lunch != []:
        dictionary['lunch_hours'] = [absence_lunch[0]['ID'],f"{absence_lunch[0]['time_start'].strftime('%H:%M')} a {absence_lunch[0]['time_end'].strftime('%H:%M')}"]
    else:
        dictionary['lunch_hours'] = None
    if others_absences != []:
        dictionary['others_absences'] = others_absences
    else:
        dictionary['others_absences'] = None
    
    return dictionary

def color_block(type, op):
    settings = OperatorSetting.objects.get(operator__ID=op)
    if type == 'availability':
        return settings.config['color_block_availability']
    elif type == 'absence':
        return settings.config['absence_block_color']
    elif type == 'lunch':
        return settings.config['color_block_lunch']
    elif type == 'os':
        return settings.config['colors_OS']

def data_in_calendar_technician(operator, month, week, year, id, day, technician):
    obj = calendar.Calendar()
    if week is not None and int(week) > 0 and day is None :
        obj_days = obj.monthdatescalendar(int(year), int(month))[int(week)-1]
    elif day is not None and week is None and int(day) > 0 and int(day) < 32:
        obj_days = [datetime.strptime(f"{day}-{month}-{year}",'%d-%m-%Y')]
    else:
        obj_days = obj.itermonthdates(int(year), int(month))
    obj_in_calendar = []
    os_in_calendar = []
    absences_in_calendar = []
    absence_lunch = []
    working_hours = 0

    for day in obj_days:
        
        schedule_technician_response = list_of_technician_availables_method(operator, day.strftime('%d-%m-%Y'), technician, 'calendar_technician')

        if len(schedule_technician_response) > 0:

            for d in schedule_technician_response:
                disponibility = Disponibility.objects.filter(ID=d['id_disponibility'])
                if len(disponibility) > 0 and disponibility != []:
                    if d['lunch_hours'] is not None:
                        a_lunch = Absence.objects.get(ID=d['lunch_hours'][0])
                        sec = 3600
                        start_time = a_lunch.time_start.strftime('%H:%M')
                        end_time = a_lunch.time_end.strftime('%H:%M') 
                        suma = start_time

                        while suma < end_time:

                            start = suma
                            end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                            suma = end.strftime('%H:%M') 

                            if suma >= end_time:
                                absence_lunch.append([start, end_time])

                            elif suma < end_time:
                                absence_lunch.append([start, suma])

                    if d['others_absences'] is not None:
                        for abs in d['others_absences']:
                            a = Absence.objects.get(ID=abs['id'])
                            sec = 3600
                            start_time = a.time_start.strftime('%H:%M')
                            end_time = a.time_end.strftime('%H:%M') 
                            suma = start_time

                            while suma < end_time:

                                start = suma
                                end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                                suma = end.strftime('%H:%M') 

                                if suma >= end_time:
                                    absences_in_calendar.append([start, end_time])

                                elif suma < end_time:
                                    absences_in_calendar.append([start, suma])

                    os_list = Os.objects.filter(
                                                    technician__ID=d['id_technician'], 
                                                    technician__operator=operator,
                                                    disponibility_hours__father=disponibility[0].ID
                                                )

                    if len(os_list) > 0:
                        for item_os in os_list:
                            sec = 3600
                            start_time = item_os.disponibility_hours.schedule_start_time.strftime('%H:%M')
                            end_time = item_os.disponibility_hours.schedule_end_time.strftime('%H:%M') 
                            suma = start_time

                            while suma < end_time:

                                start = suma
                                end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                                suma = end.strftime('%H:%M') 

                                if suma >= end_time:
                                    os_in_calendar.append([start, end_time])

                                elif suma < end_time:
                                    os_in_calendar.append([start, suma])    
                    
                    sec = 3600
                    start_time = disponibility[0].schedule_start_time.strftime('%H:%M')
                    end_time = disponibility[0].schedule_end_time.strftime('%H:%M') 
                    suma = start_time
                    flag_a = None
                    flag_b = None

                    while suma < end_time:

                        start = suma
                        end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                        suma = end.strftime('%H:%M') 

                        if suma >= end_time:
                    
                            if (
                                    [start,end_time] not in [itm for itm in os_in_calendar] and 
                                    [start,end_time] not in [itm for itm in absences_in_calendar] and 
                                    [start,end_time] not in [itm for itm in absence_lunch]
                                ):
                                if flag_a is not None:
                                    flag_b = end_time
                                working_hours = working_hours + 1
                            elif [start,end_time] in [itm for itm in absence_lunch]:
                                if flag_a is not None:
                                    flag_b = start
                                obj = {
                                        'title': 'Bloque de Almuerzo',
                                        'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                        'end': f"{day.strftime('%d-%m-%Y')} {end_time}",
                                        'color': color_block('lunch',operator)
                                    }
                                if obj not in obj_in_calendar:
                                    obj_in_calendar.append(obj)
                            elif [start,end_time] in [itm for itm in absences_in_calendar]:
                                if flag_a is not None:
                                    flag_b = start
                                obj = {
                                    
                                        'title': 'Solicitud de Ausencia',
                                        'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                        'end': f"{day.strftime('%d-%m-%Y')} {end_time}",
                                        'color': color_block('absence', operator)
                                    }
                                if obj not in obj_in_calendar:
                                    obj_in_calendar.append(obj)
                            elif [start,end_time] in [itm for itm in os_in_calendar]:
                                if flag_a is not None:
                                    flag_b = start
                                working_hours = working_hours + 1
                            if flag_a is not None and flag_b is not None:
                                obj = {
                                        'title': 'Bloque de Disponibilidad',
                                        'start': f"{day.strftime('%d-%m-%Y')} {flag_a}",
                                        'end': f"{day.strftime('%d-%m-%Y')} {flag_b}",
                                        'color': color_block('availability', operator)
                                    }
                                if obj not in obj_in_calendar:
                                    obj_in_calendar.append(obj)
                                flag_a = None
                                flag_b = None


                        elif suma < end_time:

                            if (
                                    [start,suma] not in [itm for itm in os_in_calendar] and 
                                    [start,suma] not in [itm for itm in absences_in_calendar] and 
                                    [start,suma] not in [itm for itm in absence_lunch] 
                                ):
                                if flag_a is None:
                                    flag_a = start
                                working_hours = working_hours + 1
                            elif [start,suma] in [itm for itm in absence_lunch]:
                                if flag_a is not None:
                                    flag_b = start
                                obj = {
                                            'title': 'Hora de Almuerzo',
                                            'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                            'end': f"{day.strftime('%d-%m-%Y')} {suma}",
                                            'color': color_block('lunch',operator)
                                        }
                                if obj not in obj_in_calendar:
                                    obj_in_calendar.append(obj)
                            elif [start,suma] in [itm for itm in absences_in_calendar]:
                                if flag_a is not None:
                                    flag_b = start
                                obj = {
                                        'title': 'Solicitud de Ausencia',
                                        'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                        'end': f"{day.strftime('%d-%m-%Y')} {suma}",
                                        'color': color_block('absence', operator)
                                    }
                                if obj not in obj_in_calendar:
                                    obj_in_calendar.append(obj)
                            elif [start,suma] in [itm for itm in os_in_calendar]:
                                if flag_a is not None:
                                    flag_b = start
                                working_hours = working_hours + 1
                            if flag_a is not None and flag_b is not None:
                                obj = {
                                        'title': 'Bloque de Disponibilidad',
                                        'start': f"{day.strftime('%d-%m-%Y')} {flag_a}",
                                        'end': f"{day.strftime('%d-%m-%Y')} {flag_b}",
                                        'color': color_block('availability', operator)
                                    }
                                if obj not in obj_in_calendar:
                                    obj_in_calendar.append(obj)
                                flag_a = None
                                flag_b = None

                os_in_calendar = []
                absences_in_calendar = []
                absence_lunch = []
                    
    if len(obj_in_calendar) == 0:
        raise ValidationError({'message': 'No existen técnicos disponibles para esta fecha'})

    return Response({
                        'data': obj_in_calendar,
                        'total_hours': working_hours
                    }, status=200)

class CalendarTechnicianView(APIView):

    month_param = openapi.Parameter('month', openapi.IN_QUERY, 
    description="Fecha (mes) para hacer la busqueda",
    type=openapi.TYPE_STRING)

    year_param = openapi.Parameter('year', openapi.IN_QUERY, 
    description="Fecha (año) final para hacer la busqueda",
    type=openapi.TYPE_STRING)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Id del operador a reagendar",
    type=openapi.TYPE_INTEGER)

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha (día) para hacer la busqueda",
    type=openapi.TYPE_STRING)

    week_param = openapi.Parameter('week', openapi.IN_QUERY, 
    description="Número de semana para hacer la busqueda",
    type=openapi.TYPE_STRING)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Id del técnico a buscar",
    type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[day_param, technician_param, month_param, year_param, operator_param, week_param])
    def get(self, request, *args, **kwargs):
        try:
            month = request.GET.get('month', None)
            year = request.GET.get('year', None)
            technician = request.GET.get('technician', None)
            week = request.GET.get('week',None)
            operator = request.GET.get('operator', None)
            day = request.GET.get('day', None)

            if technician == '':
                technician = None

            if month is not None and operator is not None and year is not None and week is None and day is None:
                calendar_list = data_in_calendar_technician(operator, month, week,year, technician, None, technician)
                return calendar_list
            elif month is not None and operator is not None and year is not None and week is not None and day is None:
                calendar_list = data_in_calendar_technician(operator, month, week, year, technician, None, technician)
                return calendar_list
            elif month is not None and operator is not None and year is not None and week is None and day is not None:
                calendar_list = data_in_calendar_technician(operator, month, week, year, technician, day, technician)
                return calendar_list
            else:
                raise ValidationError({'message': 'Parametros incompletos en Query'})
        except Exception as e:
            
            raise e
    

def data_in_calendar_technician_app(operator, month, week, year, id, day, technician):
    obj = calendar.Calendar()
    if week is not None and int(week) > 0 and day is None :
        obj_days = obj.monthdatescalendar(int(year), int(month))[int(week)-1]
    elif day is not None and week is None:
        obj_days = [datetime.strptime(day,'%d-%m-%Y')]
    else:
        obj_days = obj.itermonthdates(int(year), int(month))
    obj_in_calendar = []
    os_in_calendar = []
    absences_in_calendar = []
    absence_lunch = []
    you_scheduled = []
    scheduled_lunch = []
    
    working_hours = 0

    for day in obj_days:
        
        schedule_technician_response = list_of_technician_availables_method(operator, day.strftime('%d-%m-%Y'), technician, 'calendar_technician_app')

        if len(schedule_technician_response) > 0:

            for d in schedule_technician_response:

                if (
                        id is None or 
                        (
                            id is not None and d['id_technician'] == int(id)
                        )
                    ):

                    technician = Technician.objects.get(ID=d['id_technician'])

                else:
                    technician = None
                    
                if technician:
                    disponibility = Disponibility.objects.filter(ID=d['id_disponibility'])
                    if len(disponibility) > 0 and disponibility != []:
                        if d['lunch_hours'] is not None:
                            a_lunch = Absence.objects.get(ID=d['lunch_hours'][0])
                            sec = 3600
                            start_time = a_lunch.time_start.strftime('%H:%M')
                            end_time = a_lunch.time_end.strftime('%H:%M') 
                            suma = start_time

                            while suma < end_time:

                                start = suma
                                end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                                suma = end.strftime('%H:%M') 

                                if suma >= end_time:
                                    absence_lunch.append([start, end_time])

                                elif suma < end_time:
                                    absence_lunch.append([start, suma])

                        if d['others_absences'] is not None:
                            for abs in d['others_absences']:
                                a = Absence.objects.get(ID=abs['id'])
                                sec = 3600
                                start_time = a.time_start.strftime('%H:%M')
                                end_time = a.time_end.strftime('%H:%M') 
                                suma = start_time

                                while suma < end_time:

                                    start = suma
                                    end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                                    suma = end.strftime('%H:%M') 

                                    if suma >= end_time:
                                        absences_in_calendar.append([start, end_time])

                                    elif suma < end_time:
                                        absences_in_calendar.append([start, suma])

                        os_list = Os.objects.filter(
                                                        technician=technician.ID, 
                                                        technician__operator=operator,
                                                        disponibility_hours__father=disponibility[0].ID
                                                    )

                        if len(os_list) > 0:
                            for item_os in os_list:
                                sec = 3600
                                start_time = item_os.disponibility_hours.schedule_start_time.strftime('%H:%M')
                                end_time = item_os.disponibility_hours.schedule_end_time.strftime('%H:%M') 
                                suma = start_time

                                while suma < end_time:

                                    start = suma
                                    end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                                    suma = end.strftime('%H:%M') 

                                    if suma >= end_time:
                                        os_in_calendar.append([start, end_time])

                                    elif suma < end_time:
                                        os_in_calendar.append([start, suma])    
                        
                        sec = 3600
                        start_time = disponibility[0].schedule_start_time.strftime('%H:%M')
                        end_time = disponibility[0].schedule_end_time.strftime('%H:%M') 
                        suma = start_time
                        flag_a = None
                        flag_b = None

                        while suma < end_time:

                            start = suma
                            end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                            suma = end.strftime('%H:%M') 

                            if suma >= end_time:
                        
                                if (
                                        [start,end_time] not in [itm for itm in os_in_calendar] and 
                                        [start,end_time] not in [itm for itm in absences_in_calendar] and 
                                        [start,end_time] not in [itm for itm in absence_lunch]
                                    ):
                                    if flag_a is not None:
                                        flag_b = end_time
                                    working_hours = working_hours + 1
                                elif [start,end_time] in [itm for itm in absence_lunch]:
                                    if flag_a is not None:
                                        flag_b = start
                                    obj = {
                                            'title': 'Bloque de Almuerzo',
                                            'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                            'end': f"{day.strftime('%d-%m-%Y')} {end_time}",
                                            'color': '#8FD14F'
                                        }
                                    if obj not in scheduled_lunch:
                                        scheduled_lunch.append(obj)
                                elif [start,end_time] in [itm for itm in absences_in_calendar]:
                                    if flag_a is not None:
                                        flag_b = start
                                elif [start,end_time] in [itm for itm in os_in_calendar]:
                                    if flag_a is not None:
                                        flag_b = start
                                    obj = {
                                            'title': 'OS en Agenda',
                                            'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                            'end': f"{day.strftime('%d-%m-%Y')} {end_time}",
                                            'color': '#FD7D48'
                                        }
                                    if obj not in you_scheduled:
                                        you_scheduled.append(obj)
                                    working_hours = working_hours + 1
                                if flag_a is not None and flag_b is not None:
                                    obj = {
                                            'title': 'Jornada Laboral',
                                            'start': f"{day.strftime('%d-%m-%Y')} {flag_a}",
                                            'end': f"{day.strftime('%d-%m-%Y')} {flag_b}",
                                            'color': '#003CB9'
                                        }
                                    if obj not in obj_in_calendar:
                                        obj_in_calendar.append(obj)
                                    flag_a = None
                                    flag_b = None


                            elif suma < end_time:

                                if (
                                        [start,suma] not in [itm for itm in os_in_calendar] and 
                                        [start,suma] not in [itm for itm in absences_in_calendar] and 
                                        [start,suma] not in [itm for itm in absence_lunch] 
                                    ):
                                    if flag_a is None:
                                        flag_a = start
                                    working_hours = working_hours + 1
                                elif [start,suma] in [itm for itm in absence_lunch]:
                                    if flag_a is not None:
                                        flag_b = start
                                    obj = {
                                                'title': 'Hora de Almuerzo',
                                                'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                                'end': f"{day.strftime('%d-%m-%Y')} {suma}",
                                                'color': '#8FD14F'
                                            }
                                    if obj not in scheduled_lunch:
                                        scheduled_lunch.append(obj)
                                elif [start,suma] in [itm for itm in absences_in_calendar]:
                                    if flag_a is not None:
                                        flag_b = start
                                elif [start,suma] in [itm for itm in os_in_calendar]:
                                    if flag_a is not None:
                                        flag_b = start
                                    obj = {
                                            'title': 'OS en Agenda',
                                            'start': f"{day.strftime('%d-%m-%Y')} {start}",
                                            'end': f"{day.strftime('%d-%m-%Y')} {suma}",
                                            'color': '#FD7D48'
                                        }
                                    if obj not in you_scheduled:
                                        you_scheduled.append(obj)
                                    working_hours = working_hours + 1
                                if flag_a is not None and flag_b is not None:
                                    obj = {
                                                                'title': 'Jornada Laboral',
                                                                'start': f"{day.strftime('%d-%m-%Y')} {flag_a}",
                                                                'end': f"{day.strftime('%d-%m-%Y')} {flag_b}",
                                                                'color': '#003CB9'
                                                            }
                                    if obj not in obj_in_calendar:
                                        obj_in_calendar.append(obj)
                                    flag_a = None
                                    flag_b = None

                
                os_in_calendar = []
                absences_in_calendar = []
                absence_lunch = []


                    
    if len(obj_in_calendar) == 0:
        raise ValidationError({'message': 'No existen técnicos disponibles para esta fecha'})

    return Response({
                        'working_day_data': obj_in_calendar,
                        'lunch': scheduled_lunch,
                        'you_schedule': you_scheduled,
                        'total_hours': working_hours
                    }, status=200)

class CalendarTechnicianAppView(APIView):

    month_param = openapi.Parameter('month', openapi.IN_QUERY, 
    description="Fecha (mes) para hacer la busqueda",
    type=openapi.TYPE_STRING)

    year_param = openapi.Parameter('year', openapi.IN_QUERY, 
    description="Fecha (año) final para hacer la busqueda",
    type=openapi.TYPE_STRING)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Id del operador a reagendar",
    type=openapi.TYPE_INTEGER)

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha (día) para hacer la busqueda",
    type=openapi.TYPE_STRING)

    week_param = openapi.Parameter('week', openapi.IN_QUERY, 
    description="Número de semana para hacer la busqueda",
    type=openapi.TYPE_STRING)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Id del técnico a reagendar",
    type=openapi.TYPE_INTEGER)

    def get(self, request, *args, **kwargs):
        try:
            month = request.GET.get('month', None)
            year = request.GET.get('year', None)
            technician = request.GET.get('technician', None)
            week = request.GET.get('week',None)
            operator = request.GET.get('operator', None)
            day = request.GET.get('day', None)

            if month is not None and operator is not None and year is not None and week is None and day is None and technician is not None:
                calendar_list = data_in_calendar_technician_app(operator, month, week,year, technician, None, technician)
                return calendar_list
            elif month is not None and operator is not None and year is not None and week is not None and day is None and technician is not None:
                calendar_list = data_in_calendar_technician_app(operator, month, week, year, technician, None, technician)
                return calendar_list
            elif month is not None and operator is not None and year is not None and week is None and day is not None and technician is not None:
                calendar_list = data_in_calendar_technician_app(operator, month, week, year, technician, day, technician)
                return calendar_list
            else:
                raise ValidationError({'message': 'Parametros incompletos en Query'})
        except Exception as e:
            
            raise e
        
def absences_data(day_format, absence, dictionary, list_availables_technicians, technician, id_disponibility):
    if len(absence) > 0:
        if (day_format.strftime('%d-%m-%Y') in [itm['time_start'].strftime('%d-%m-%Y') for itm in absence if itm['time_start'].strftime('%d-%m-%Y') == day_format.strftime('%d-%m-%Y') and itm['status'] == 1 and (itm['type'] == 0 or itm['type'] == 1 or itm == 2)]):
            absence_lunch = [itm for itm in absence if itm['time_start'].strftime('%d-%m-%Y') == day_format.strftime('%d-%m-%Y') and itm['status'] == 1 and itm['type'] == 0]
            list_absences = []
            others_absences = [itm for itm in absence if itm['time_start'].strftime('%d-%m-%Y') == day_format.strftime('%d-%m-%Y') and itm['status'] == 1 and (itm['type'] == 1 or itm['type'] == 2)]
            if len(others_absences) > 0:
                for i in others_absences:
                    list_absences.append({
                                            'id': i['ID'],
                                            'start': i['time_start'].strftime('%d-%m-%Y %H:%M'),
                                            'end': i['time_end'].strftime('%d-%m-%Y %H:%M'),
                                        })
                    
            list_availables_technicians.append(dictionary_obj(dictionary,absence_lunch,technician,id_disponibility,list_absences))
        else:
            list_availables_technicians.append(dictionary_obj(dictionary,[],technician,id_disponibility,[]))
    else:
        list_availables_technicians.append(dictionary_obj(dictionary,[],technician,id_disponibility,[]))
        
def list_of_technician_availables_method(operator, day, technician, type, id_category):

    day_format = datetime.strptime(day, '%d-%m-%Y')
    if technician is None:
        schedule = Schedule.objects.filter( 
                                            schedule_start_date__lte=day_format,
                                            technician__operator=operator
                                            ).filter(Q(schedule_end_date__gte=day_format) | 
                                                     Q(schedule_end_date__isnull=True)).select_related('technician')
    else:
        schedule = Schedule.objects.filter( 
                                            schedule_start_date__lte=day_format,
                                            technician__operator=operator,
                                            technician = technician
                                            ).filter(Q(schedule_end_date__gte=day_format) | 
                                                     Q(schedule_end_date__isnull=True)).select_related('technician')

    list_availables_technicians = []
    number_day = datetime.strptime(day, '%d-%m-%Y').weekday() 
    
    if len(schedule) > 0:

        for item in schedule:

            dictionary = {}
            disponibility = item.disponibility.values('ID', 'schedule_day', 'hours_unassigned', 'schedule_status')
            absence = item.absence.values('ID', 'type','status', 'time_start', 'time_end')
            holiday = item.Holiday.values('ID', 'day')
            technician = {'id': item.technician.ID, 'name': item.technician.name, 'last_name': item.technician.last_name, 'categories': item.technician.categories.values_list('ID')}

            if len(disponibility) > 0:

                for d in disponibility:

                    if type == 'disponibility' or type == 'calendar_technician':

                        if (
                                d['schedule_status'] == 0 and 
                                d['hours_unassigned'] is not None and  
                                to_seconds(d['hours_unassigned']) > 0 and 
                                d['schedule_day'] == number_day and  
                                day_format.strftime('%d-%m-%Y') not in [itm['day'].strftime('%d-%m-%Y') for itm in holiday if day_format.strftime('%d-%m-%Y') == itm['day'].strftime('%d-%m-%Y')]
                            ):

                            if type=='disponibility' and int(id_category) in [item[0] for item in technician['categories']]:

                                absences_data(day_format,absence, dictionary, list_availables_technicians, technician, d['ID'])

                            elif type == 'calendar_technician': 

                                absences_data(day_format,absence, dictionary, list_availables_technicians, technician, d['ID'])
                    
                    elif type == 'calendar_technician_app':

                        if (
                                d['schedule_status'] == 0 and 
                                d['hours_unassigned'] is not None and         
                                d['schedule_day'] == number_day and 
                                day_format.strftime('%d-%m-%Y') not in [itm['day'].strftime('%d-%m-%Y') for itm in holiday if day_format.strftime('%d-%m-%Y') == itm['day'].strftime('%d-%m-%Y')]
                            ):

                            absences_data(day_format,absence, dictionary, list_availables_technicians, technician, d['ID'])
                            

    return list_availables_technicians

def list_of_hours_method(data_list,seconds):

    list_of_hour_range = []
    time = []
    hours_absence = []
    hours_availabilities_created = []

    for item in data_list:

        availability_information = Disponibility.objects.get(ID=item['id_disponibility'])
        availabilities_created = Disponibility.objects.filter(father__ID=item['id_disponibility'], schedule_status=1)

        for a in availabilities_created:

            sec = seconds
            start_time = a.schedule_start_time.strftime('%H:%M')
            end_time = a.schedule_end_time.strftime('%H:%M') 
            suma = start_time

            if seconds/3600 > 1:
                sec = 1800

            while suma < end_time:

                start = suma
                end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                suma = end.strftime('%H:%M') 

                if suma >= end_time:
                    time.append(f"{start} a {end_time}")
                    hours_availabilities_created.append([f"{start} a {end_time}",item['id_technician']])


                elif suma < end_time:
                    time.append(f"{start} a {suma}")
                    hours_availabilities_created.append([f"{start} a {suma}",item['id_technician']])

        
        if item['lunch_hours'] is not None:
            absence_information = Absence.objects.get(ID=item['lunch_hours'][0])
            time.append(f"{absence_information.time_start.strftime('%H:%M')} a {absence_information.time_end.strftime('%H:%M')}")
            hours_absence.append([f"{absence_information.time_start.strftime('%H:%M')} a {absence_information.time_end.strftime('%H:%M')}",item['id_technician']])
        
        if item['others_absences'] is not None:
            for i in item['others_absences']:
                abs = Absence.objects.get(ID=i['id'])
                sec = seconds
                start_time = abs.time_start.strftime('%H:%M')
                end_time = abs.time_end.strftime('%H:%M') 
                suma = start_time

                if seconds/3600 > 1:
                    sec = 1800

                while suma < end_time:

                    start = suma
                    end = datetime.strptime(suma, '%H:%M') + timedelta(0,sec)
                    suma = end.strftime('%H:%M') 

                    if suma >= end_time:
                        time.append(f"{start} a {end_time}")
                        hours_absence.append([f"{start} a {end_time}",item['id_technician']])


                    elif suma < end_time:
                        time.append(f"{start} a {suma}")
                        hours_absence.append([f"{start} a {suma}",item['id_technician']])

        if (availability_information.hours_unassigned is not None and 
            to_seconds(availability_information.hours_unassigned) >= seconds):

            start_time = availability_information.schedule_start_time.strftime('%H:%M')
            end_time = availability_information.schedule_end_time.strftime('%H:%M') 
            suma = start_time

            while suma < end_time:

                start = suma
                end = datetime.strptime(suma, '%H:%M') + timedelta(0,seconds)
                suma = end.strftime('%H:%M') 

                if suma >= end_time:
                    
                    if (f"{start} a {end_time}" not in time or
                       (
                            f"{start} a {end_time}" in time and 
                            f"{start} a {end_time}" in [itm[0] for itm in hours_absence if itm[1]!=item['id_technician']] or
                            f"{start} a {end_time}" in [itm[0] for itm in hours_availabilities_created if itm[1]!=item['id_technician']] 

                        ) and 
                        start != absence_information.time_start.strftime('%H:%M') and 
                        end_time != absence_information.time_end.strftime('%H:%M')):

                        if seconds/3600 > 1:

                            sec = 1800
                            start_a = start
                            end_a = end_time
                            suma_a = start_a
                            exists = []

                            while suma_a < end_a:

                                s = suma_a
                                e = datetime.strptime(suma_a, '%H:%M') + timedelta(0,sec)
                                suma_a = e.strftime('%H:%M') 

                                if s >= end_a:
    
                                    if f"{s} a {end_a}" not in time:
                                        
                                        exists = False

                                    else: 
                                        exists = True

                                elif s < end_a:
                                
                                    if f"{s} a {suma_a}" not in time:

                                        exists.append(False)

                                    else: 
                                        exists.append(True)

                            if not True in exists:

                                list_of_hour_range.append({ 
                                                                'technician_id': item['id_technician'],
                                                                'hours': f"{start} a {end_time}",
                                                                'disponibilidad': availability_information.ID,
                                                                'start_time': start,
                                                                'end_time': end_time,
                                                                'color': '#0060F8'
                                                            })
                                time.append(f"{start} a {end_time}")

                        else:

                            list_of_hour_range.append({ 
                                                            'technician_id': item['id_technician'],
                                                            'hours': f"{start} a {end_time}",
                                                            'disponibilidad': availability_information.ID,
                                                            'start_time': start,
                                                            'end_time': end_time,
                                                            'color': '#0060F8'
                                                        })
                            time.append(f"{start} a {end_time}")


                elif suma < end_time:

                    if (f"{start} a {suma}" not in time or
                        (
                            f"{start} a {suma}" in time and 
                            f"{start} a {suma}" in [itm[0] for itm in hours_absence if itm[1]!=item['id_technician']] or
                            f"{start} a {suma}" in [itm[0] for itm in hours_availabilities_created if itm[1]!=item['id_technician']] 

                        ) and 
                        start != absence_information.time_start.strftime('%H:%M') and 
                        suma != absence_information.time_end.strftime('%H:%M')):

                        if seconds/3600 > 1:

                            sec = 1800
                            start_a = start
                            end_a = suma
                            suma_a = start_a
                            exists = []

                            while suma_a < end_a:

                                s = suma_a
                                e = datetime.strptime(suma_a, '%H:%M') + timedelta(0,sec)
                                suma_a = e.strftime('%H:%M') 

                                if s >= end_a:

                                    if f"{s} a {end_a}" not in time:
                                        
                                        exists.append(False)

                                    else: 
                                        exists.append(True)

                                elif s < end_a:

                                    if f"{s} a {suma_a}" not in time:

                                        exists.append(False)

                                    else: 
                                        exists.append(True)

                            if not True in exists:

                                list_of_hour_range.append({ 
                                                                'technician_id': item['id_technician'],
                                                                'hours': f"{start} a {suma}",
                                                                'disponibilidad': availability_information.ID,
                                                                'start_time': start,
                                                                'end_time': suma,
                                                                'color' : '#0060F8'
                                                            })
                                time.append(f"{start} a {suma}")

                        else:

                                list_of_hour_range.append({ 
                                                                'technician_id': item['id_technician'],
                                                                'hours': f"{start} a {suma}",
                                                                'disponibilidad': availability_information.ID,
                                                                'start_time': start,
                                                                'end_time': suma,
                                                                'color': '#0060F8'
                                                            })
                                time.append(f"{start} a {suma}")
                        
    return list_of_hour_range


class CreateSegmentedAvailabilityView(APIView):

    disponibility_param = openapi.Parameter('id_disponibility', openapi.IN_QUERY, 
    description="Disponibilidad Padre para realacionar la busqueda",
    type=openapi.TYPE_STRING)

    start_time_param = openapi.Parameter('start_time', openapi.IN_QUERY, 
    description="Hora inicial para crear la disponibilidad  para hacer la busqueda",
    type=openapi.TYPE_STRING)

    end_time_param = openapi.Parameter('end_time', openapi.IN_QUERY, 
    description="Operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    date_param = openapi.Parameter('date', openapi.IN_QUERY, 
    description="Día para crear la disponibilidad",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[disponibility_param,start_time_param,end_time_param, date_param])
    def get(self, request, *args, **kwargs):

        try:

            start = request.GET.get('start_time', None)
            end = request.GET.get('end_time', None)
            date = request.GET.get('date', None)
            father_id = request.GET.get('id_disponibility', None)
            father = Disponibility.objects.filter(ID=father_id)

            if (father_id is None or 
                start is None or 
                end is None):
                raise ValidationError({'message':'Campos nulos para crear objeto'})


            if father.count() > 0:
                father = father[0]

            if datetime.strptime(start,'%H:%M') > datetime.strptime(end,'%H:%M'):
                swap = start
                start = end
                end = swap

            direction = Direction.objects.get(id=father.dir.id)
            
            child = Disponibility.objects.create(   
                                            schedule_day = father.schedule_day,   
                                            schedule_start_time=datetime.strptime(start,'%H:%M'),
                                            schedule_end_time=datetime.strptime(end,'%H:%M'),
                                            date = datetime.strptime(date, '%d-%m-%Y'),
                                            dir = direction,
                                            schedule_status = 0,
                                            father = father
                                            )
            child.schedule_status = 1
            child.save()

            difference_unassigned_hours = restar_hora(father.hours_unassigned.strftime('%H:%M:%S'), str(child.hours_unassigned))
            difference_unassigned_hours = datetime.strptime(difference_unassigned_hours, '%H:%M:%S')
        
            if to_seconds(difference_unassigned_hours) >= 60:
                
                father.hours_unassigned = difference_unassigned_hours
                father.save()

            else:

                father.hours_unassigned = datetime.strptime("00:00:00", '%H:%M:%S')
                father.save()

            if father.hours_unassigned is not None and to_seconds(father.hours_unassigned) <= 0:

                father.schedule_status = 1
                father.save()

            return Response({'id_disponibility_created': child.ID},status=200)

        except Exception as e:

            raise e
class ListOfAvailableTechniciansView(APIView):
    
    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha para hacer la busqueda",
    type=openapi.TYPE_STRING)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Id del técnico",
    type=openapi.TYPE_INTEGER)

    category_param = openapi.Parameter('category', openapi.IN_QUERY, 
    description="Id de la categoria",
    type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[day_param,operator_param, technician_param, category_param])
    def get(self, request, *args, **kwargs):

        try:

            day = request.GET.get('day')
            operator = request.GET.get('operator')
            technician = request.GET.get('technician', None)
            id_category = request.GET.get('category', None)
            operator_model = Operator.objects.get(ID=operator)

            response = list_of_technician_availables_method(operator_model.ID, day,technician, 'disponibility', id_category)

            if len(response)>0:
                return Response({'list_of_technicians_availables': response},status=200)
            else:
                if technician is not None:
                    raise ObjectDoesNotExist({'message':f"Objeto no encontrado para la fecha {day} y técnico {technician}"})   
                else:
                    raise ObjectDoesNotExist({'message':f"Objeto no encontrado para la fecha {day}"})     
                
        except Exception as e:

            raise e


class RangeOfHoursAvailableView(APIView):

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha para hacer la busqueda",
    type=openapi.TYPE_STRING)

    category_param = openapi.Parameter('category', openapi.IN_QUERY, 
    description="Id de la categoria",
    type=openapi.TYPE_INTEGER)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Id del técnico",
    type=openapi.TYPE_INTEGER)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[day_param, category_param, technician_param])
    def get(self, request, *args, **kwargs):

        try:

            now = datetime.now()
            day = request.GET.get('day',None)
            technician = request.GET.get('technician', None)
            category = request.GET.get('category', None)
            time = Category.objects.get(ID=int(category))
            operator = request.GET.get('operator', time.os_type.operator)
            schedule_technician_response = list_of_technician_availables_method(operator, day, technician, 'disponibility', category)
            seconds = int(time.duration) * 60
            day_format=datetime.strptime(day, '%d-%m-%Y')
            list_of_hour_range = []

            if len(schedule_technician_response) == 0:

                raise ValidationError({'message': 'Objeto no encontrado'})

            if day_format.strftime('%d-%m-%Y') >= now.strftime('%d-%m-%Y'):

                list_of_hour_range = list_of_hours_method(schedule_technician_response,seconds)

                if len(list_of_hour_range) < 1:

                    if technician is not None:

                        raise ObjectDoesNotExist({'message':f"No existe un listado de horas para la fecha {day} y técnico {technician}"})
                    
                    else:
                        
                        raise ObjectDoesNotExist({'message':f"No existe un listado de horas para la fecha {day}"})


                return Response({'list_of_hour_range':list_of_hour_range}, status=200)

            else:

                raise ValidationError({'message': 'Fecha inválida para agendar'})
            
        except Exception as e:

            raise e