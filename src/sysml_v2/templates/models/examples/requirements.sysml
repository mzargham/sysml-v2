package VehicleRequirements {
    doc /* Example: Requirements for the vehicle system. */

    import VehicleModel::*;

    // --- Requirement Definitions ---

    requirement def MassRequirement {
        doc /* The total vehicle mass shall not exceed the specified limit. */

        attribute massLimit : Mass;

        subject vehicle : Vehicle;

        require constraint {
            vehicle.totalMass <= massLimit
        }
    }

    requirement def PerformanceRequirement {
        doc /* The engine shall deliver at least the specified power output. */

        attribute minPower : ISQ::PowerValue;

        subject engine : Engine;

        require constraint {
            engine.maxPower >= minPower
        }
    }

    // --- Requirement Usages ---

    requirement vehicleMassReq : MassRequirement {
        doc /* The vehicle shall weigh no more than 2000 kg. */

        attribute :>> massLimit = 2000 [SI::kg];
    }

    requirement enginePowerReq : PerformanceRequirement {
        doc /* The engine shall produce at least 150 kW. */

        attribute :>> minPower = 150 [SI::kW];
    }

    // --- Satisfaction ---

    satisfy vehicleMassReq by VehicleModel::testVehicle;
}
