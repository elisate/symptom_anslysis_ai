from django.urls import path
from .views import patient_predict
from .patientRegister import (register_user,get_all_users,
                              get_user_by_id,update_user_by_id)
from .patientLogin import login_user
from .Pridiction_Res_view import (get_prediction_result,get_prediction_by_id,
                                  get_all_predictions,
                                  get_predictions_by_user_id)
from resourceFinder.hospitalView import (
    create_hospital,get_all_hospitals
)
from resourceFinder.doctorView import (create_doctor,get_doctors_by_hospital,
                                       get_doctor_by_id,
                                       get_all_doctors,delete_doctor_by_id,
                                       update_doctor_by_id)
from resourceFinder.patientView import (create_patient,
                                        get_patients_by_hospital,
                                        get_all_patients,get_patient_by_id,
                                        delete_patient_by_id,
                                        update_patient_by_id)
from resourceFinder.hospital_schedule_view import (create_or_update_hospital_schedule,
                                                   get_hospital_schedule,update_schedule_slot,
                                                   delete_schedule_slot,
                                                   get_hospital_schedule_by_name
                                                   )
from resourceFinder.appointment_view import (request_hospital_appointment,
                                             get_appointments_by_hospital,
                                             get_appointments_by_user_id,
                                             get_all_pending_appointments_by_hospital,
                                             update_appointment_status,
                                             get_appointment_by_id,
                                             assign_doctor_to_appointment,
                                             get_appointments_by_doctor_id)
from resourceFinder.contactView import createContact
from resourceFinder.treatmentView import create_treatment

from resourceFinder.specialViews.patientTreatedByDoctor import patients_and_treatments_by_doctor
from resourceFinder.specialViews.loadPatientDataByNatId import (load_patient_data,
                                                                patient_info_and_treatments,
                                                                get_patient_by_national_id)
from resourceFinder.specialViews.loadPatientDataByNatId import get_patient_by_id
from resourceFinder.specialViews.forgetPin import request_password_reset,reset_password_with_otp
urlpatterns = [
    #------------------AUTHENTICATION----------------------
    path("/register",register_user),
    path("/login",login_user),
    path("/loadPatientData",load_patient_data),
    path("/patientGetDataByHisId/<str:patient_id>/",patient_info_and_treatments),
    path("/getuserById/<str:user_id>",get_user_by_id),
    path("/updateuserById/<str:user_id>",update_user_by_id),
    #---------------------------PATIENT------------------------
    path('/patient/getById/<str:patient_id>',get_patient_by_id),
    path('/patient/deleteById/<str:patient_id>', delete_patient_by_id),
    path('/patient/UpdateById/<str:patient_id>', update_patient_by_id),
    #------------------ARTIFICIAL INTELLIGENCE---------------
    path("/resourceFinder",patient_predict),
    path("/liveResultPredicted",get_prediction_result),
    path("/liveResultPredicted/predictions/<str:prediction_id>/",get_prediction_by_id),
    path('/predictions/user/<str:user_id>/', get_predictions_by_user_id),    #----------------HOSPITAL------------------
    path("/hospitals/create", create_hospital),
    path("/hospitals/create",get_all_hospitals),
    #---------------DOCTOR------------
    path("/doctor/create",create_doctor),
    path("/doctor/getDoctorById/<str:doctor_id>",get_doctor_by_id),
    path("/doctor/getDoctorByHospitalId/<str:hospital_id>",get_doctors_by_hospital),
    path("/patient/create",create_patient),
    path("/doctor/treating",create_treatment),
    path("/DeleteById/<str:doctor_id>",delete_doctor_by_id),
    path("/UpdateById/<str:doctor_id>",update_doctor_by_id),
    #-----------------SPECIAL DOCTOR END POINT------------------------
    path("/doctor/patientTreated/<str:doctor_id>",patients_and_treatments_by_doctor),
    #----------------HOSPITAL SCHEDULE---------------
    path("/schedule/create",create_or_update_hospital_schedule),
    path('/schedule/get/<str:hospital_id>/',get_hospital_schedule),
    path("/schedule/update_day",update_schedule_slot),
    path("/schedule/delete_slot",delete_schedule_slot),
    path("/schedule/getByHospitalName/<str:hospital_name>/",get_hospital_schedule_by_name),
    
    #--------------APPOINTMENT-------------------------
    path("/Appointment/createRequest",request_hospital_appointment),
    path("/Appointment/getAppointmentByHospId/<hospital_id>",get_appointments_by_hospital),
    path("/Appointment/getAppointmentByUserId/<str:user_id>",get_appointments_by_user_id),
    path("/Appointment/getAppointmentById/<str:appointment_id>",get_appointment_by_id),
    path("/Appointment/getPatientByHospId/<hospital_id>",get_patients_by_hospital),
    path("/appointment/getAllPendingAppointmentsByHospId/<str:hospital_id>",get_all_pending_appointments_by_hospital),
    path('/appointment/update-status/<str:appointment_id>',update_appointment_status),
    path('/appointment/assignToDoctor-status',assign_doctor_to_appointment),
    path('/appointment/by-doctor-id/<str:doctor_id>/', get_appointments_by_doctor_id),

    #---------------------------------- CONTACT---------------------
    path("/contact/createContact",createContact),

    # -----------------SUPER ADMIN-------------------------
     path('/getAllHospitals', get_all_hospitals),
     path("/getAllUsers",get_all_users),
     path("/getAllDoctors",get_all_doctors),
     path("/getAllPredictions",get_all_predictions),
     path("/getAllPatients",get_all_patients),
     path("/GetLoaded/<str:national_id>",get_patient_by_national_id),
     path("/PatientId/<str:patient_id>",get_patient_by_id),
     path("/requestReset",request_password_reset),
     path("/ChangePassword",reset_password_with_otp)

    
]


