from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from resourceFinder.medical_ai.scheduleModel import HospitalSchedule, TimeSlot
from resourceFinder.medical_ai.hospitalModel import Hospital
import json
import traceback
def parse_timeslots(day_data):
    if not isinstance(day_data, list):
        raise ValueError("Each day's schedule must be a list of timeslot dictionaries.")
    return [TimeSlot(**slot) for slot in day_data if isinstance(slot, dict)]

def create_or_update_hospital_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hospital_id = data.get('hospital_id')
            print("Hospital ID:", hospital_id)

            hospital = Hospital.objects(id=hospital_id).first()
            print("Hospital Found:", hospital)

            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            existing_schedule = HospitalSchedule.objects(hospital=hospital).first()
            timeslot_fields = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            parsed_data = {day: parse_timeslots(data.get(day, [])) for day in timeslot_fields}
            print("Parsed Data:", parsed_data)

            if existing_schedule:
                for day, slots in parsed_data.items():
                    setattr(existing_schedule, day, slots)
                existing_schedule.save()
                return JsonResponse({"message": "Schedule updated successfully."}, status=200)
            else:
                new_schedule = HospitalSchedule(hospital=hospital, **parsed_data)
                new_schedule.save()
                return JsonResponse({"message": "Schedule created successfully."}, status=201)

        except Exception as e:
            print("Error occurred:", str(e))
            print(traceback.format_exc())
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

def get_hospital_schedule(request, hospital_id):
    if request.method == 'GET':
        try:
            hospital = Hospital.objects(id=hospital_id).first()

            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()

            if not schedule:
                return JsonResponse({"error": "Schedule not found"}, status=404)

            return JsonResponse({
                "hospital_id": str(hospital.id),
                "schedule": {
                    "monday": [slot.to_mongo().to_dict() for slot in schedule.monday],
                    "tuesday": [slot.to_mongo().to_dict() for slot in schedule.tuesday],
                    "wednesday": [slot.to_mongo().to_dict() for slot in schedule.wednesday],
                    "thursday": [slot.to_mongo().to_dict() for slot in schedule.thursday],
                    "friday": [slot.to_mongo().to_dict() for slot in schedule.friday],
                    "saturday": [slot.to_mongo().to_dict() for slot in schedule.saturday],
                    "sunday": [slot.to_mongo().to_dict() for slot in schedule.sunday],
                }
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_schedule_slot(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            hospital_id = data.get("hospital_id")
            day = data.get("day")
            new_slot = data.get("slot")  # Single slot (dict)
            slot_index = data.get("index")  # Optional index
            slots = data.get("slots")  # Optional list of slots

            if not (hospital_id and day):
                return JsonResponse({"error": "Missing hospital_id or day"}, status=400)

            hospital = Hospital.objects(id=hospital_id).first()
            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()
            if not schedule:
                return JsonResponse({"error": "Schedule not found"}, status=404)

            if day not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                return JsonResponse({"error": "Invalid day name"}, status=400)

            # Update a single slot (by index or append)
            if new_slot:
                day_slots = getattr(schedule, day)
                timeslot = TimeSlot(**new_slot)

                if slot_index is not None and isinstance(slot_index, int):
                    if 0 <= slot_index < len(day_slots):
                        day_slots[slot_index] = timeslot
                    else:
                        return JsonResponse({"error": "Invalid slot index"}, status=400)
                else:
                    day_slots.append(timeslot)

                setattr(schedule, day, day_slots)

            # Replace all slots for a day
            elif slots is not None and isinstance(slots, list):
                timeslot_objs = [TimeSlot(**slot) for slot in slots if isinstance(slot, dict)]
                setattr(schedule, day, timeslot_objs)

            else:
                return JsonResponse({"error": "Either 'slot' or 'slots' must be provided"}, status=400)

            schedule.save()
            return JsonResponse({"message": f"{day.capitalize()} schedule updated successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only PUT method is allowed"}, status=405)

@csrf_exempt
def delete_schedule_slot(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            hospital_id = data.get("hospital_id")
            day = data.get("day")
            slot_index = data.get("index")

            if not all([hospital_id, day, isinstance(slot_index, int)]):
                return JsonResponse({"error": "Missing or invalid hospital_id, day, or index"}, status=400)

            hospital = Hospital.objects(id=hospital_id).first()
            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()
            if not schedule:
                return JsonResponse({"error": "Schedule not found"}, status=404)

            if day not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                return JsonResponse({"error": "Invalid day name"}, status=400)

            day_slots = getattr(schedule, day)
            if 0 <= slot_index < len(day_slots):
                del day_slots[slot_index]
                setattr(schedule, day, day_slots)
                schedule.save()
                return JsonResponse({"message": f"Slot at index {slot_index} on {day.capitalize()} deleted successfully"}, status=200)
            else:
                return JsonResponse({"error": "Invalid slot index"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only DELETE method is allowed"}, status=405)


@csrf_exempt
def get_hospital_schedule_by_name(request, hospital_name):
    if request.method == 'GET':
        try:
            hospital = Hospital.objects(hospital_name__iexact=hospital_name).first()

            if not hospital:
                return JsonResponse({"error": "Hospital not found"}, status=404)

            schedule = HospitalSchedule.objects(hospital=hospital).first()

            if not schedule:
                return JsonResponse({"error": "Schedule not found"}, status=404)

            return JsonResponse({
                "hospital_id": str(hospital.id),
                "schedule": {
                    "monday": [slot.to_mongo().to_dict() for slot in schedule.monday],
                    "tuesday": [slot.to_mongo().to_dict() for slot in schedule.tuesday],
                    "wednesday": [slot.to_mongo().to_dict() for slot in schedule.wednesday],
                    "thursday": [slot.to_mongo().to_dict() for slot in schedule.thursday],
                    "friday": [slot.to_mongo().to_dict() for slot in schedule.friday],
                    "saturday": [slot.to_mongo().to_dict() for slot in schedule.saturday],
                    "sunday": [slot.to_mongo().to_dict() for slot in schedule.sunday],
                }
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
