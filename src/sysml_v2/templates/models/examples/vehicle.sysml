package VehicleModel {
    doc /* Example: A simple vehicle part decomposition in SysML v2. */

    // --- Attribute Definitions ---

    attribute def Mass :> ISQ::MassValue;
    attribute def Length :> ISQ::LengthValue;

    // --- Part Definitions ---

    part def Vehicle {
        doc /* Top-level vehicle system. */

        attribute totalMass : Mass;

        part chassis : Chassis;
        part engine : Engine;
        part transmission : Transmission;
        part wheels : Wheel[4];
    }

    part def Chassis {
        attribute mass : Mass;
        attribute length : Length;
    }

    part def Engine {
        attribute mass : Mass;
        attribute displacement : ISQ::VolumeValue;
        attribute maxPower : ISQ::PowerValue;

        port fuelIn : FuelPort;
        port driveOut : TorquePort;
    }

    part def Transmission {
        attribute mass : Mass;
        attribute gearCount : ScalarValues::Integer;

        port driveIn : TorquePort;
        port driveOut : TorquePort;
    }

    part def Wheel {
        attribute mass : Mass;
        attribute diameter : Length;
    }

    // --- Port Definitions ---

    port def FuelPort;
    port def TorquePort;

    // --- Example Usage (instantiation) ---

    part testVehicle : Vehicle {
        attribute :>> totalMass = 1500 [SI::kg];

        part :>> engine {
            attribute :>> mass = 200 [SI::kg];
            attribute :>> displacement = 2.0 [SI::L];
        }

        part :>> chassis {
            attribute :>> mass = 400 [SI::kg];
            attribute :>> length = 4.5 [SI::m];
        }
    }
}
