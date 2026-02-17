### Requirement Analysis

#### 1. When the app is started, the user is presented with the main menu, which allows the user to (1) enter or edit current job details, (2) enter job offers, (3) adjust the comparison settings, or (4) compare job offers (disabled if no job offers were entered yet).

Even the assignment not required GUI, I realize this requirement by adding some `<<GUI>>` classes which serves as the entry point and main controller. It contains:
- `<<GUI>> MainMenu` - present main menu to the user
- `<<GUI>> CurrentJobDetailed` - present/enter/edit current job detailed
- `<<GUI>> OfferedJob` - present/enter/edit job offered detailed
- `<<GUI>> ComparisonSetting` - adjust comparison settings
- `<<GUI>> JobComparison` - compare job offers. The business logic to enable/disable the compare option is handled by checking if `jobOffers_isEmpty()` before allowing the comparison operation

#### 2. When choosing to enter current job details, a user will:
**a. Be shown a user interface to enter (if it is the first time) or edit all the details of their current job, which consists of: Title, Company, Location (entered as city and state), Cost of living in the location (expressed as an index), Yearly salary, Yearly bonus, Stock Option Shares (Whole number, assumes 3-year vesting period and $1 stock value), Wellness Stipend ($0-$1200 Inclusive annually), Life Insurance (Percentage of Yearly Salary as an integer: 0 – 10 inclusive), Personal Development Fund ($0 to $6000 inclusive annually)**

The job details are represented by an abstract `Job` base class with two concrete subclasses: `CurrentJob` (for the user's existing job) and `JobOffer` (for offered positions). This inheritance hierarchy provides type safety and makes the distinction between current job and offers explicit at the design level.

The `Job` base class contains the following attributes:
- `title: String`
- `company: String`
- `location: Location` - Composition relationship with Location class
- `costOfLivingIndex: int`
- `yearlySalary: double`
- `yearlyBonus: double`
- `stockOptionShares: int`
- `wellnessStipend: double` (constrained 0-1200)
- `lifeInsurance: int` (constrained 0-10)
- `personalDevelopmentFund: double` (constrained 0-6000)

The `Location` class is a separate entity with:
- `city: String`
- `state: String`

The `JobComparisonApp` provides:
- `enterCurrentJob(): void` - Method to create/edit current job
- `saveCurrentJob(job: Job): void` - Saves the current job

The GUI will handle the display and input collection, while the validation logic for ranges (e.g., wellness stipend 0-1200) would be implemented in setter methods or validation methods in the `Job` class.

**b. Be able to either save the job details or cancel and exit without saving, returning in both cases to the main menu.**

**Design Realization:**
This is handled by the `enterCurrentJob()` and `saveCurrentJob()` methods in `JobComparisonApp`. If the user cancels, the method returns to `showMainMenu()` without calling `saveCurrentJob()`. The actual UI flow (save/cancel buttons) is handled by the GUI layer.

#### 3. When choosing to enter job offers, a user will:
**a. Be shown a user interface to enter all the details of the offer, which are the same ones listed above for the current job.**

**Design Realization:**
Job offers are represented by the `JobOffer` class which inherits from `Job`, ensuring consistency while providing type distinction. The `JobComparisonApp` provides:
- `enterJobOffer(): void` - Method to create a new job offer
- `addJobOffer(offer: JobOffer): void` - Adds a job offer to the list

**b. Be able to either save the job offer details or cancel.**

**Design Realization:**
Similar to requirement 2b, the `enterJobOffer()` method handles the flow, and `addJobOffer()` is only called if the user saves. The GUI handles the save/cancel interaction.

**c. Be able to (1) enter another offer, (2) return to the main menu, or (3) compare the offer (if they saved it) with the current job details (if present).**

**Design Realization:**
After saving a job offer through `addJobOffer()`, the application flow returns control to allow:
- Calling `enterJobOffer()` again for another offer
- Calling `showMainMenu()` to return to main menu
- Calling `compareOfferWithCurrent(job: Job): void` to compare the saved offer with current job

The comparison is only enabled if both the offer was saved and `currentJob` is not null.

#### 4. When adjusting the comparison settings, the user can assign integer weights to: Yearly salary, Yearly bonus, Stock Option Shares, Wellness Stipend, Life Insurance, Personal Development Fund. NOTE: These factors should be integer-based from 0 (no interest/don't care) to 9 (highest interest). Default value for all weights: 1

**Design Realization:**
The `ComparisonSettings` class manages the weights with the following attributes:
- `salarWeight: int` (default 1, range 0-9)
- `bonusWeight: int` (default 1, range 0-9)
- `stockWeight: int` (default 1, range 0-9)
- `wellnessWeight: int` (default 1, range 0-9)
- `lifeInsuranceWeight: int` (default 1, range 0-9)
- `developmentFundWeight: int` (default 1, range 0-9)

Methods include:
- `setWeights(salary, bonus, stock, wellness, insurance, fund): void` - Sets all weights
- `getTotalWeight(): int` - Returns sum of all weights for normalization

The `JobComparisonApp` provides:
- `adjustSettings(): void` - Method to modify settings
- `saveSettings(settings: ComparisonSettings): void` - Persists settings

Default values are initialized in the `ComparisonSettings` constructor.

**If no weights are assigned, all factors are considered equal. The user must be able to either save the comparison settings or cancel; both will return the user to the main menu.**

**Design Realization:**
The default value of 1 for all weights ensures equal consideration. The save/cancel behavior is handled similarly to job entry methods, with the GUI managing the interaction and `saveSettings()` only called on save confirmation.

#### 5. When choosing to compare job offers, a user will:
**a. Be shown a list of job offers, displayed as Title and Company, ranked from best to worst (see below for details), and including the current job (if present), clearly indicated.**

**Design Realization:**
The `JobComparator` class handles ranking logic:
- `rankJobs(jobs: List<Job>, settings: ComparisonSettings): List<Job>` - Returns jobs sorted by score

The `JobComparisonApp` provides:
- `compareJobs(): void` - Initiates comparison view
- `getRankedJobs(): List<Job>` - Returns sorted list including current job

The `Job` class provides:
- `getTitle(): String` and `getCompany(): String` for display
- A flag or method to identify if it's the current job

**b. Select two jobs to compare and trigger the comparison.**

**Design Realization:**
The `JobComparisonApp` provides:
- `compareTwoJobs(job1: Job, job2: Job): void` - Compares selected jobs

The GUI handles the selection interface and passes the two selected jobs to this method.

**c. Be shown a table comparing the two jobs, displaying, for each job: Title, Company, Location, Yearly salary adjusted for cost of living, Yearly bonus adjusted for cost of living, Stock Option Shares (SOS), Wellness Stipend (WS), Life Insurance (LI), Personal Development Fund (PDF), Job Score (JS)**

**Design Realization:**
The `Job` class provides methods to calculate adjusted values:
- `getAdjustedSalary(): double` - Returns `yearlySalary / costOfLivingIndex * 100`
- `getAdjustedBonus(): double` - Returns `yearlyBonus / costOfLivingIndex * 100`
- Getter methods for all other attributes

The `JobComparator` class provides:
- `calculateJobScore(job: Job, settings: ComparisonSettings): double` - Calculates weighted score

The GUI retrieves these values for display in the comparison table.

**d. Be offered to perform another comparison or go back to the main menu.**

**Design Realization:**
After `compareTwoJobs()` completes, the application flow allows the user to either call `compareJobs()` again or `showMainMenu()`. This navigation is managed by the `JobComparisonApp` controller logic.

#### 6. When ranking jobs, a job's score is computed as the weighted average of: AYS + AYB + (SOS/3) + WS + (LI/100 * YS) + PDF

**Design Realization:**
The `JobComparator` class contains the `calculateJobScore(job: Job, settings: ComparisonSettings): double` method that implements the formula:

```
totalWeight = sum of all weights
JS = (salarWeight/totalWeight * AYS) + 
     (bonusWeight/totalWeight * AYB) + 
     (stockWeight/totalWeight * SOS/3) + 
     (wellnessWeight/totalWeight * WS) + 
     (lifeInsuranceWeight/totalWeight * LI/100 * YS) + 
     (developmentFundWeight/totalWeight * PDF)
```

Where:
- AYS = `job.getAdjustedSalary()`
- AYB = `job.getAdjustedBonus()`
- SOS = `job.getStockOptionShares()`
- WS = `job.getWellnessStipend()`
- LI = `job.getLifeInsurance()`
- YS = `job.getYearlySalary()`
- PDF = `job.getPersonalDevelopmentFund()`

The weights are retrieved from the `ComparisonSettings` object.

#### 7. The user interface must be intuitive and responsive.

**Design Realization:**
This requirement is not directly represented in the design, as it will be handled entirely within the GUI implementation. The design provides clean interfaces (public methods) that the GUI can call, making it easier to create an intuitive and responsive UI.

#### 8. For simplicity, you may assume there is a single system running the app (no communication or saving between devices is necessary).

**Design Realization:**
This requirement informs the design but does not require specific representation. The design assumes single-user, in-memory storage through the collections in `JobComparisonApp` (currentJob, jobOffers, settings). No network or cross-device synchronization classes are needed. Persistence, if needed, would be handled by a simple data access layer (CRUD operations) that is not shown in this design as it doesn't add to the logical structure.

### Design Assumptions

1. **Data Validation:** Range validation for constrained fields (e.g., wellnessStipend 0-1200, lifeInsurance 0-10) is assumed to be implemented in the `Job` class setter methods or through validation methods, though not explicitly shown in the UML to keep the diagram focused on primary functionality.

2. **Persistence:** Since requirement 8 assumes a single system, we assume in-memory storage during runtime. If persistence between sessions is needed, it would be implemented through a simple data access layer performing CRUD operations on the existing classes, which doesn't need to be shown in this logical design.

3. **Current Job Flag:** The current job is stored separately as `currentJob` in `JobComparisonApp` rather than as a flagged item in the jobOffers list. This makes it clear and prevents accidental modification. When ranking all jobs, the current job is included in the comparison if it exists.

4. **GUI Separation:** All user interface elements (menus, forms, tables, buttons) are intentionally omitted from this design as they are implementation details of the presentation layer. The design focuses on the application logic and data model.

5. **Cost of Living Adjustment:** The cost of living index is used as a divisor with the formula `(salary / index) * 100` to normalize salaries across locations. An index of 100 represents the baseline.

6. **Immutability:** Once a job offer is saved, it's assumed to be immutable. Editing would require removing and re-adding. The current job, however, can be edited through the `enterCurrentJob()` method.

### Design Rationale

**Class Structure:**
- **JobComparisonApp:** Central controller that manages application flow and holds references to all data. This serves as the entry point and coordinates between different operations.

- **Job (Abstract):** Base class that encapsulates all job-related data. The class provides methods to calculate adjusted values, keeping business logic encapsulated. Making it abstract prevents direct instantiation and enforces the use of concrete subclasses.

- **CurrentJob:** Concrete subclass representing the user's existing job. Inherits all attributes and methods from Job. The type distinction makes it clear when methods operate on the current job versus offers.

- **JobOffer:** Concrete subclass representing offered positions. Inherits all attributes and methods from Job. Separating this from CurrentJob provides type safety and prevents accidentally treating offers as the current job.

- **Location:** Separated into its own class as it's a distinct concept with multiple attributes (city, state). This follows the principle of single responsibility and makes the design more maintainable.

- **ComparisonSettings:** Dedicated class for managing weights keeps the settings separate from job data and comparison logic. This allows settings to be modified independently and makes the design more modular.

- **JobComparator:** Utility class that handles comparison logic. Separating this from the Job class follows the Single Responsibility Principle - Job manages data, JobComparator manages comparison algorithms. This also makes it easier to modify the ranking algorithm without changing the Job class.

**Relationships:**
- CurrentJob and JobOffer both inherit from Job (generalization/inheritance relationship)
- JobComparisonApp has aggregation relationships with both CurrentJob (0..1) and JobOffer instances (0..*), and composition with ComparisonSettings
- Job has a composition relationship with Location (a job must have a location)
- JobComparator has a dependency on Job and ComparisonSettings (uses them but doesn't own them)

**Aggregation vs Composition:**
- Both CurrentJob and JobOffer use **aggregation** (hollow diamond) because jobs exist in the real world independently of the app. The app collects and compares job data, but doesn't own or control the lifecycle of the jobs themselves.
- ComparisonSettings uses **composition** (filled diamond) because the settings are created and managed by the app, with no meaning outside the app's context.
- Location uses **composition** with Job because a location is an integral part of a job's definition and has no independent identity in this domain.

**Inheritance Rationale:**
While CurrentJob and JobOffer don't add new attributes or override methods, the inheritance structure provides several benefits:
1. **Type Safety:** The compiler/type system can distinguish between current job and offers, preventing errors like accidentally replacing the current job with an offer
2. **Code Intent:** The design clearly communicates that these are related but distinct concepts
3. **Future Extensibility:** If requirements change (e.g., offers need acceptance status, current job needs start date), the structure is already in place
4. **Design Clarity:** Explicitly shows the relationship between different types of jobs in the domain model

This design is implementation-neutral and can be realized in various programming languages and frameworks while maintaining the logical structure of the application.
