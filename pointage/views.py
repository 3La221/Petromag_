import calendar
from datetime import timedelta
import locale
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from pointage.forms import *
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time
from django.contrib.auth import logout
from django.core.paginator import Paginator , EmptyPage
from .models import *

def pointage2(request,ID):
    station = Station.objects.get(id=ID)
    instances=Employe.objects.filter(station=station)
    date=datetime.now().date()  
    f_date = date - timedelta(days=5)
    print(date)
    date_range = [f_date + timedelta(days=i) for i in range(15)]
    if request.method == 'POST':
        credentials = service_account.Credentials.from_service_account_file(
        './petropointage-b1093416d578.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        )

        # Specify the ID of your Google Sheet
        spreadsheet_id = '15BSWan9Olz9WisDThGlGESdcZPw4GGIvnLyayFIP74I'
        service = build('sheets', 'v4', credentials=credentials)
        
        for i in instances:
            ranges_and_values={}
            for date in date_range:
                cell=find_cell(date)
                choice=request.POST.get(f'{i.ID}_{date}')
               
                sheet_range = f"{i.ID}!{cell}"
                code=Code_Employe.objects.filter(employe=i,date=date)
                if  choice == "" :
                    if code.exists():
                        ranges_and_values[sheet_range]=[['']]
                        code.delete()
                    else:
                        continue
                elif choice == None :
                    continue
                else:
                    if code.exists():
                        code.delete()
                    code_emp=Code_Employe()
                    code_emp.employe=i
                    code_emp.date=date 
                    code_emp.code=Code.objects.get(pk=choice)
                    code_emp.save()
                    ranges_and_values[sheet_range] = [[f"{choice}"]]
            requests = [
                {
                    "range": range_,
                    "values": values,
                }
                for range_, values in ranges_and_values.items()
                ]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"valueInputOption": "RAW", "data": requests},
            ).execute()
            
        return redirect(main_view,i.ID)
    else:
        tmp = {}
        res = {}
        for i in instances :
                codes_emp = Code_Employe.objects.filter(employe=i)
                tmp = {}
                for d in date_range:
                    try :
                        e = codes_emp.get(date=d)
                        
                        tmp[str(d)] = e 
                    except:
                        tmp[str(d)] = ""
                
                res[i.ID] = tmp
        print("res",res)
        codes=Code.objects.all()
        context={'date':date,'instances':instances,'date_range':date_range,'codes':codes,'res':res,'today':date}
        return render(request,'pointage.html',context)    

def logout_view(request):
    logout(request)
    return redirect("/")

def find_cell(date):
    if (date.day <=25):
        alphabet=chr(ord('B') + (date.day)%26 -1)
    else:
        alphabet="A"+chr(ord('A') + (date.day)%26)
    return (f"{alphabet}{date.month+13}")


def pointage(request,ID):
    if request.user.profile.station.id != ID  and (request.user.profile.da != 1) :
        return redirect("menu_view")
    instances=Employe.objects.filter(station=ID)
    date=datetime.now().date()
    date_range = [date + timedelta(days=i) for i in range(15)]

    if request.method == 'POST':
        credentials = service_account.Credentials.from_service_account_file(
        './petropointage-b1093416d578.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        )

        # Specify the ID of your Google Sheet
        spreadsheet_id = '15BSWan9Olz9WisDThGlGESdcZPw4GGIvnLyayFIP74I'
        service = build('sheets', 'v4', credentials=credentials)
        
        for i in instances:
            for date in date_range:
                cell=find_cell(date)
                choice=request.POST.get(f'{i.ID}_{date}')
                sheet_range = f"{i.ID}!{cell}"
                values = [[f"{choice}"]]
                body = {'values': values}
                service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=sheet_range,
                valueInputOption='RAW', body=body
                ).execute()
        return redirect("main_view",i.ID)
    else:
        context={'date':date,'instances':instances,'date_range':date_range}
        return render(request,'pointage.html',context)       

def main_view(request,ID):
    i=Employe.objects.get(ID=ID)
    return render(request,'main.html',{'result':i})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("menu_view")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('menu_view')  # Redirect to home page after successful login
        else:
            # Handle invalid login
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')


# def menu_view(request):
#     if not request.user.is_authenticated:
#         return redirect("login")
#     id = request.user.profile.station.id
    
#     return render(request, 'menu.html',{'id':id})

def menu_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    id = request.user.profile.station.id
    if request.user.profile.da == 1 and request.GET.get('station'):
        print(request.GET.get('station'))
        id=request.GET.get('station')  
    station = Station.objects.get(id=id)
    return render(request, 'menu.html',{'id':id ,'station':station})


def add_employe(request,ID):
    #the first part is a script that takes information from a sheet and create instances for each employe in that sheet If you want to use it you should modify model so that it won't check for pk
    if request.user.profile.station.id != ID and (request.user.profile.da != 1) :
        return redirect("menu_view")
    if request.user.profile.da == 1:
        if request.method == 'POST':
            form = EmployeFormForDg(request.POST)
            if form.is_valid():
                user=form.save()
                return redirect('table_employe',ID)
        else :
            form = EmployeFormForDg()
    else:
        if request.method == 'POST':
            form = EmployeForm(request.POST)
            if form.is_valid():
                user=form.save()
                user.station=ID
                user.save()
                return redirect('table_employe',ID)
        else:
            form = EmployeForm()
            
    return render (request, 'add_employe.html', {'form': form,'id':ID})

def table_employe(request,ID):
    if request.user.profile.station.id != ID  and (request.user.profile.da != 1) :
        return redirect("menu_view")
    instances=Employe.objects.filter(station=ID)
    return render(request,'table_employe.html',{'id':ID,'instances':instances,'da':request.user.profile.da})

# def employee_search(request,ID):
#     searched=request.GET.get('query','')
#     action=request.GET.get('action')
#     if searched.isdigit():
#         i=Employe.objects.filter(pk=searched , ID_Station_id=ID)
#         i=i.first()
#         if i :
#             if action=='update':
#                 return redirect (update_employe,i.ID)
#             elif action=='sheet_pointage':
#                 return redirect(main_view,i.ID)
#             else:
#                 return redirect(pointage_mois,i.ID)
            
#     message ='ID incorrect '
#     instances=Employe.objects.filter(ID_Station_id=ID)
#     return render(request,'table_employe.html',{'id':ID,'instances':instances,'message':message})
        
def pointage_mois(request,ID):
    # if request.user.profile.station.id != ID and (request.user.profile.da == 1) :
    #     return redirect("menu_view")
    instance=Employe.objects.get(pk=ID)
    return render(request,'mois_form.html',{'instance':instance})



def affichage_mois(request,ID):

    month_names_french = {
        0: 'janvier',
        1: 'janvier',
        2: 'février',
        3: 'mars',
        4: 'avril',
        5: 'mai',
        6: 'juin',
        7: 'juillet',
        8: 'août',
        9: 'septembre',
        10: 'octobre',
        11: 'novembre',
        12: 'décembre',
    }

    i=Employe.objects.get(pk=ID)
    mois=request.POST.get('month')
    credentials = service_account.Credentials.from_service_account_file(
    './petropointage-b1093416d578.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets'],
    )

    # Create a service using the credentials
    service = build('sheets', 'v4', credentials=credentials)
    source_spreadsheet_id = '15BSWan9Olz9WisDThGlGESdcZPw4GGIvnLyayFIP74I'
    dest_spreadsheet_id = '1mcaMIJmwYZV-TytMXaRlrNQwZHjEp2yCP7W1GSyjaSk'

    range_to_clear = "template!B15:AF15"
    service.spreadsheets().values().clear(
        spreadsheetId=dest_spreadsheet_id,
        range=range_to_clear
    ).execute()
    born_inf=int(mois)
    born_sup=(int(mois)+1) if (int(mois)+1) <=12 else 1
# Specify the sheet name and range to copy
    ranges = [f"{ID}!AO4:AT4",f"{ID}!Q{born_inf+13}:AG{born_inf+13}",f"{ID}!B{born_sup+13}:AG{born_sup+13}"]
# Iterate through each range and retrieve values
    result=service.spreadsheets().values().batchGet(
        spreadsheetId=source_spreadsheet_id,
        ranges=ranges,
        ).execute()
    list1 = result['valueRanges'][1]['values']
    list1[0].pop()
    list2 = result['valueRanges'][2]['values']
    list2f=list2[0][:14]
    merged_list = list1[0] + list2f
    ranges_and_values = {
        'template!G14:W15':[[f'16 {month_names_french[int(mois)]} - 15 {month_names_french[(int(mois)+1)%13]}']],
        'template!AO4:AT4': result['valueRanges'][0]['values'],
        'template!B18:AF18': [merged_list],
        "template!AG6:AJ6": [[f'{i.Date_Recrutement}']],
        "template!B8:N8": [[f"{i.Fonction}"]],
        "template!U6:X6": [[f"{i.ID}"]],
        "template!B6:N6": [[f"{i.Nom}"]],  # Update B2:N6 with "Value1"
        "template!B7:N7": [[f"{i.Prenom}"]],  # Update B7:N7 with "Value2"
        "template!AG8:AJ8": [["" if f"{i.Date_Detach}" == 'None' else f"{i.Date_Detach}"]],
        "template!B10:X10": [["" if f"{i.Adresse}" == 'None' else f"{i.Adresse}"]],
        "template!AG9:AM9": [["" if f"{i.Affect_Origin}" == 'None' else f"{i.Affect_Origin}"]],
        "template!AG10:AJ10": [["" if f"{i.Situation_Familliale}" == 'None' else f"{i.Situation_Familliale}"]],
        "template!AG11:AH11": [["" if f"{i.Nbr_Enfants}" == 'None' else f"{i.Nbr_Enfants}"]],
        # Add more ranges and values as needed
    }
    requests = [
        {
            'range':range_,
            'values':values,
        }
        for range_,values in ranges_and_values.items()
    ]

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=dest_spreadsheet_id,
        body={"valueInputOption": "RAW", "data": requests},
        ).execute()
    return render(request,'mois.html',{'ID':i.station_id})

def update_employe(request,ID):
    employe=Employe.objects.get(ID=ID)
    if request.method == 'POST':
        form=EmployeForm(request.POST,instance=employe)
        if form.is_valid():
            form.save()
            return redirect(table_employe,employe.station.id)
    else:
        form=EmployeForm(instance=employe)
        return render(request,'update_employe.html',{'i':employe,'form':form})
# Create your views here.
