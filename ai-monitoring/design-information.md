### Requirement Analysis

#### 1. When the app is started, the user is presented with the main menu, which allows the user to (1) enter or edit current job details, (2) enter job offers, (3) adjust the comparison settings, or (4) compare job offers (disabled if no job offers were entered yet).

Even the assignment not required GUI, I realize this requirement by adding some `<<GUI>>` classes which serves as the entry point and main controller. It contains:
- `<<GUI>> MainMenu` - present main menu to the user
- `<<GUI>> CurrentJobDetailed` - present/enter/edit current job detailed
- `<<GUI>> OfferedJob` - present/enter/edit job offered detailed
- `<<GUI>> ComparisonSettings` - adjust comparison settings
- `<<GUI>> JobComparison` - compare job offers. The business logic to enable/disable the compare option is handled by checking if `jobOffers_isEmpty():bool` before allowing the comparison operation

#### 2. When choosing to enter current job details, a user will:
**a. Be shown a user interface to enter (if it is the first time) or edit all the details of their current job, which consists of: Title, Company, Location (entered as city and state), Cost of living in the location (expressed as an index), Yearly salary, Yearly bonus, Stock Option Shares (Whole number, assumes 3-year vesting period and $1 stock value), Wellness Stipend ($0-$1200 Inclusive annually), Life Insurance (Percentage of Yearly Salary as an integer: 0 – 10 inclusive), Personal Development Fund ($0 to $6000 inclusive annually)**

The job details are represented by an abstract `Job` base class with two concrete subclasses: `CurrentJob` (for the user's existing job) and `OfferedJob` (for offered positions). This inheritance hierarchy provides type safety and makes the distinction between current job and offers explicit at the design level matching to the different GUI

The `Job` base class contains the following attributes:
- `title: String`
- `company: String`
- `location: Location` - Composition relationship with Location class
- `livingCost: String` - Validation rule: expressed as an index
- `yearlySalary: Decimal`
- `yearlyBonus: Decimal`
- `stockOptionShares: Interger`
- `wellnessStipend: Decimal` (constrained 0-1200)
- `lifeInsurance: Interger` (constrained 0-10)
- `personalDevelopmentFund: Decimal` (constrained 0-6000)

The `Job` base class contains the following operations:
- `Add(job):void` - Add current job
- `Edit(job):void` - Save current job

The `Location` class is a separate entity with:
- `city: String`
- `state: String`

**b. Be able to either save the job details or cancel and exit without saving, returning in both cases to the main menu.**

This is handled by the `EnterCurrentJob()` and `SaveCurrentJob()` methods in `<<GUI>> CurrentJobDetailed` and `Add(job)` method in `CurrentJob` class (inhertied from `Job` class). If the user cancels, the method returns to `showMainMenu()` without calling `SaveCurrentJob()`. The actual UI flow (save/cancel buttons) is handled by the GUI layer.

#### 3. When choosing to enter job offers, a user will:
**a. Be shown a user interface to enter all the details of the offer, which are the same ones listed above for the current job.**

Job offers are represented by the `OfferedJob` class which inherits from `Job`. The `<<GUI>> OfferedJob` provides:
- `AddJobOffer(): void` - Adds a job offer to the list by calling `Add(job)` method in `OfferedJob` class. With inhertied from `Job` class, the`OfferedJob` class whose attribute are the same to the `CurrentJob` class

**b. Be able to either save the job offer details or cancel.**

Similar to requirement 2b, the `EnterOfferedJob()` method handles the flow, and `AddJobOffer()` of `<<GUI>> OfferedJob` are only called if the user saves. The GUI handles the save/cancel interaction.

**c. Be able to (1) enter another offer, (2) return to the main menu, or (3) compare the offer (if they saved it) with the current job details (if present).**

At `<<GUI>> OfferedJob`, after saving a job offer through `AddJobOffer():void`, the application flow returns control to allow:
- Calling `EnterJobOffer():void` again for another offer
- Calling `ShowMainMenu():void` to return to main menu
- Calling `CompareWithCurrent(JobOffer): void` to compare the saved offer with current job

#### 4. When adjusting the comparison settings, the user can assign integer weights to: Yearly salary, Yearly bonus, Stock Option Shares, Wellness Stipend, Life Insurance, Personal Development Fund. NOTE: These factors should be integer-based from 0 (no interest/don't care) to 9 (highest interest). Default value for all weights: 1

The `ComparisonSettings` class manages the weights with the following attributes:
- `yearlySalaryWeight: Interger` (default 1, range 0-9)
- `yearlyBonusWeight: Interger` (default 1, range 0-9)
- `stockOptionSharesWeight: Interger` (default 1, range 0-9)
- `wellnessWeight: Interger` (default 1, range 0-9)
- `lifeInsuranceWeight: Interger` (default 1, range 0-9)
- `personalDevelopmentFundWeight: Interger` (default 1, range 0-9)

Methods include:
- `Add(settings): void` - Sets all settings with contrainst: if no weights are assigned, all factors are equal
- `Get(): ComparisionSetting` - Returns settings

The `<<GUI>> ComparisonSettings` provides:
- `AdjustSettings(): void` - Method to modify settings
- `SaveSettings(): void` - Persists settings

#### 5. When choosing to compare job offers, a user will:
**a. Be shown a list of job offers, displayed as Title and Company, ranked from best to worst (see below for details), and including the current job (if present), clearly indicated.**

The `<<GUI>> JobComparison` provides `RankJobs(): List<Job>` method allow user ranks job offer by calling `JobComparator` class which provides:
- `RankJobs(): List<Job>` - Returns sorted list from best to worst and including the current job

**b. Select two jobs to compare and trigger the comparison.**

The `<<GUI>> JobComparison` provides `CompareJob(Job1, Job2): void` method allow user compares job offer by calling method of `JobComparator` to caculate score of each job for comparision
- `CalculateJobScore(Job, ComparisonSetting): Decimal` - Trigger comparison caculate the job with comparison settings

**c. Be shown a table comparing the two jobs, displaying, for each job: Title, Company, Location, Yearly salary adjusted for cost of living, Yearly bonus adjusted for cost of living, Stock Option Shares (SOS), Wellness Stipend (WS), Life Insurance (LI), Personal Development Fund (PDF), Job Score (JS)**

This is not represented in my design, as it will be handled entirely within the GUI implementation. The GUI retrieves these values for display in the comparison table.

**d. Be offered to perform another comparison or go back to the main menu.**

In the `<<GUI>> JobComparison`, after `CompareJobs(Job1,Job2)` completes, the user is able to to either call `CompareJobs(Job1,Job2)` again or `showMainMenu()` to back to main menu.

#### 6. When ranking jobs, a job's score is computed as the weighted average of: AYS + AYB + (SOS/3) + WS + (LI/100 * YS) + PDF

The `JobComparator` class contains the `CalculateJobScore(Job, ComparisonSettings): Decimal` method that implements the formula. The weights are retrieved from the `ComparisonSettings` object by using `Get(): ComparisionSetting` of `ComparisonSettings` class

#### 7. The user interface must be intuitive and responsive.

This is not represented in my design, as it will be handled entirely within the GUI implementation.

#### 8. For simplicity, you may assume there is a single system running the app (no communication or saving between devices is necessary).

As this is assumption for sumilicity, this is not represented in my design, as it will be handled entirely within the GUI implementation.
