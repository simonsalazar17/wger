# Interaction Diagrams

## Record Body Weight

This diagram expands the SSD event `recordBodyWeight(weightValue, measurementDate)`.

```mermaid
sequenceDiagram
    autonumber
    actor User as Fitness User
    participant V as weightEntries:WeightEntryViewSet
    participant S as serializer:WeightEntrySerializer
    participant P as profile:UserProfile
    participant C as Category
    participant M as measurement:Measurement

    User->>V: recordBodyWeight(weightValue, measurementDate)
    V->>S: is_valid(weightValue, measurementDate)
    S->>P: read weight_unit
    P-->>S: preferredWeightUnit
    S->>S: validate_weight(weightValue)

    alt weightValue is outside the limits for preferredWeightUnit
        S-->>V: ValidationError
        V-->>User: HTTP 400, allowed weight range
    else weightValue is valid
        S-->>V: validated_data
        V->>P: read weight_unit
        P-->>V: preferredWeightUnit
        V->>C: get_or_create_body_weight(user, unit=preferredWeightUnit)

        alt official body-weight category exists
            C-->>V: existing category:Category
        else official body-weight category does not exist
            C->>C: get_or_create_official(user, BODY_WEIGHT, name, unit)
            C-->>V: new category:Category
        end

        V->>S: save(category, extra_data={unit})
        S->>M: objects.create(validated_data, category, extra_data)
        M-->>S: saved measurement:Measurement
        S-->>V: saved measurement:Measurement
        V-->>User: HTTP 201, savedMeasurement
    end
```

Participants are implemented by `WeightEntryViewSet` in `wger/weight/api/views.py`, `WeightEntrySerializer` in `wger/weight/api/serializers.py`, `UserProfile` in `wger/core/models/profile.py`, and `Category` and `Measurement` in `wger/measurements/models/`.

## Add Meal Item

This diagram expands the SSD event `addMealItem(mealId, ingredientId, amount, weightUnit)`.

```mermaid
sequenceDiagram
    autonumber
    actor User as Fitness User
    participant V as mealItems:MealItemViewSet
    participant S as serializer:MealItemSerializer
    participant M as meal:Meal
    participant P as plan:NutritionPlan
    participant I as ingredient:Ingredient
    participant MI as mealItem:MealItem

    User->>V: addMealItem(mealId, ingredientId, amount, weightUnit)
    V->>V: _check_owner_permission(request)
    V->>M: objects.get(pk=mealId)
    M-->>V: meal:Meal
    V->>M: get_owner_object()
    M-->>V: plan:NutritionPlan
    V->>P: read user_id
    P-->>V: ownerId

    alt plan is not owned by the authenticated user
        V-->>User: HTTP 403, permission denied
    else plan is owned by the authenticated user
        V->>S: is_valid(mealId, ingredientId, amount, weightUnit)
        S->>I: objects.get(pk=ingredientId)
        I-->>S: ingredient:Ingredient

        alt amount is outside 1 through 1000
            S-->>V: ValidationError
            V-->>User: HTTP 400, invalid amount
        else meal-item data is valid
            S-->>V: validated_data
            V->>S: save(order=1)
            S->>MI: objects.create(meal, ingredient, amount, weightUnit, order)
            MI-->>S: saved mealItem:MealItem
            S-->>V: saved mealItem:MealItem
            V-->>User: HTTP 201, mealItem
        end
    end
```

Participants are implemented by `MealItemViewSet` in `wger/nutrition/api/views.py`, `MealItemSerializer` in `wger/nutrition/api/serializers.py`, and `Meal`, `NutritionPlan`, `Ingredient`, and `MealItem` in `wger/nutrition/models/`.

## Log Cardio Activity

This diagram follows the successful web form submission from the final-project feature. The view is a Django function rather than a controller class; `CardioLogForm` validates the submitted model fields and the view assigns the authenticated owner before saving.

```mermaid
sequenceDiagram
    autonumber
    actor User as Authenticated User
    participant V as overview (wger/manager/views/cardio.py)
    participant F as CardioLogForm
    participant M as CardioLog
    participant DB as Django ORM / database

    User->>V: POST activity, date, duration, distance, unit, notes
    V->>F: bind request.POST
    V->>F: is_valid()
    F-->>V: valid form and cleaned model fields
    V->>F: save(commit=False)
    F-->>V: unsaved CardioLog instance
    V->>M: assign user=request.user
    V->>M: save()
    M->>DB: INSERT CardioLog row
    DB-->>M: persisted row
    M-->>V: saved activity
    V-->>User: redirect to cardio overview; activity appears in owner-filtered list
```

The main success path is implemented in `wger/manager/views/cardio.py`, `wger/manager/forms.py`, `wger/manager/models/cardio.py`, and `wger/manager/templates/manager/cardio/overview.html`. Model validation is shared with the API serializer in `wger/manager/api/serializers.py`.
