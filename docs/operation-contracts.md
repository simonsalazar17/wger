# Operation Contracts

## Contract 1: Create Workout Routine

**Operation:** `createRoutine(name, description, startDate, endDate)`

**Cross-references:** Use case Create Workout Routine

**Preconditions:**

- A `Person` representing the authenticated fitness user exists.
- `startDate` is on or before `endDate`.
- The period from `startDate` through `endDate` does not exceed the permitted routine duration.

**Postconditions:**

- A `WorkoutRoutine` instance was created.
- `WorkoutRoutine.name` was set to `name`.
- `WorkoutRoutine.description` was set to `description`.
- `WorkoutRoutine.startDate` was set to `startDate`.
- `WorkoutRoutine.endDate` was set to `endDate`.
- An ownership association was formed between the `Person` and the `WorkoutRoutine`.

## Contract 2: Add Meal Item

**Operation:** `addMealItem(mealId, ingredientId, amount, weightUnit)`

**Cross-references:** Use case Create Nutrition Plan

**Preconditions:**

- A `Person` representing the authenticated fitness user exists.
- A `Meal` identified by `mealId` exists within a `NutritionPlan` owned by that `Person`.
- An `Ingredient` identified by `ingredientId` exists.
- `amount` is between 1 and 1,000.
- `weightUnit` is valid for the selected `Ingredient`.

**Postconditions:**

- A `MealItem` instance was created.
- `MealItem.amount` was set to `amount`.
- `MealItem.weightUnit` was set to `weightUnit`.
- An association was formed between the `MealItem` and the `Meal`.
- An association was formed between the `MealItem` and the `Ingredient`.
- `NutritionPlan.totalEnergy` was set to the energy total calculated from all associated `MealItem` instances.
- `NutritionPlan.totalProtein` was set to the protein total calculated from all associated `MealItem` instances.
- `NutritionPlan.totalCarbohydrates` was set to the carbohydrate total calculated from all associated `MealItem` instances.
- `NutritionPlan.totalFat` was set to the fat total calculated from all associated `MealItem` instances.
- `NutritionPlan.totalFiber` was set to the fiber total calculated from all associated `MealItem` instances.
- `NutritionPlan.totalSodium` was set to the sodium total calculated from all associated `MealItem` instances.

## Contract 3: Record Body Weight

**Operation:** `recordBodyWeight(weightValue, measurementDate)`

**Cross-references:** Use case Track Body Weight

**Preconditions:**

- A `Person` representing the authenticated fitness user exists.
- `Person.preferredWeightUnit` is set to kilograms or pounds.
- An official body-weight `MeasurementCategory` is associated with the `Person`.
- `weightValue` is within the permitted range for `Person.preferredWeightUnit`.

**Postconditions:**

- A `BodyWeightMeasurement` instance was created.
- `BodyWeightMeasurement.value` was set to `weightValue`.
- `BodyWeightMeasurement.dateTime` was set to `measurementDate`.
- `BodyWeightMeasurement.recordedUnit` was set to `Person.preferredWeightUnit`.
- An association was formed between the `BodyWeightMeasurement` and the official body-weight `MeasurementCategory`.
