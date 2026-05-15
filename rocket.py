import numpy as np
from atmosphere import USStandardAtmosphere1976

class Rocket:
    def __init__(self):
        # Physical Properties (from user images)
        self.m_s1_prop = 48000.0  # kg
        self.m_s1_dry = 4000.0    # kg
        self.m_s2_prop = 7000.0    # kg
        self.m_s2_dry = 800.0     # kg
        self.m_payload = 1350.0   # kg
        
        self.diameter = 2.0       # m
        self.ref_area = np.pi * (self.diameter / 2)**2
        self.total_height = 30.0   # m
        
        # Engine Properties (Stage 1)
        self.s1_sl_thrust = 1.5e6  # N (1.5 MN)
        self.s1_sl_isp = 295.0     # s
        self.s1_vac_isp = 320.0    # s
        self.RE = 6356766.0        # m (Earth radius for gravity turn)
        
        # Derived values for Stage 1
        self.g0 = 9.80665
        self.m_dot_max = self.s1_sl_thrust / (self.g0 * self.s1_sl_isp)
        self.s1_vac_thrust = self.m_dot_max * self.g0 * self.s1_vac_isp
        
        # Structural Limits
        self.limit_q = 40000.0      # Pa (Design limit for Max-Q)
        self.limit_axial_g = 6.0    # g
        self.limit_bending = 1.5e5  # Nm (Simplified bending moment limit)
        
    def get_mass(self, propellant_burned):
        """Calculate current mass based on propellant consumed."""
        total_liftoff_mass = self.m_s1_prop + self.m_s1_dry + self.m_s2_prop + self.m_s2_dry + self.m_payload
        return total_liftoff_mass - propellant_burned

    def get_cg_position(self, propellant_burned):
        """
        Model CG shift. As propellant burns, CG typically moves upward in Stage 1.
        Simplified model: moves from 40% height to 60% height.
        """
        burn_fraction = propellant_burned / self.m_s1_prop
        return self.total_height * (0.4 + 0.2 * burn_fraction)

    def get_cp_position(self, mach):
        """
        Center of Pressure position. Shifts during transonic flight.
        Simplified model: moves aft at supersonic speeds.
        """
        if mach < 0.8:
            return self.total_height * 0.3  # Forward
        elif mach < 1.2:
            return self.total_height * (0.3 + 0.1 * (mach - 0.8) / 0.4)
        else:
            return self.total_height * 0.4  # Further aft

    def get_thrust(self, altitude, throttle):
        """Calculate thrust at given altitude and throttle (0.0 to 1.0)."""
        _, p_amb, _, _ = USStandardAtmosphere1976.get_properties(altitude)
        p_sl = 101325.0
        
        # Linear interpolation of thrust between SL and Vac based on ambient pressure
        # T(p) = T_vac - (T_vac - T_sl) * (p / p_sl)
        thrust_full = self.s1_vac_thrust - (self.s1_vac_thrust - self.s1_sl_thrust) * (p_amb / p_sl)
        return thrust_full * throttle

    def get_cd(self, mach):
        """
        Drag coefficient as a function of Mach number.
        Models the transonic drag rise (Prandtl-Glauert singularity / wave drag).
        """
        if mach < 0.8:
            return 0.15
        elif mach < 1.0:
            # Transonic rise
            return 0.15 + 0.3 * (mach - 0.8) / 0.2
        elif mach < 1.2:
            # Transonic peak and slight drop
            return 0.45 - 0.1 * (mach - 1.0) / 0.2
        elif mach < 5.0:
            # Supersonic decay
            return 0.35 * np.exp(-0.2 * (mach - 1.2)) + 0.1
        else:
            # Hypersonic floor
            return 0.18

    def calculate_loads(self, q, velocity, mass, accel, aoa_deg):
        """
        Calculate structural loads.
        - Axial load: Tension/Compression from thrust and drag.
        - Bending moment: From aerodynamic side loads (q * alpha).
        """
        # Axial acceleration in Gs
        axial_g = accel / self.g0
        
        # Simplified Bending Moment: M = q * Area * L * sin(alpha)
        # L is distance between CP and CG
        # We'll use a placeholder for AoA if not provided by simulation.
        # Wind effects will modify AoA.
        
        # Side force Coefficient approx: Cy = 2 * sin(alpha) (Newtonian or slender body theory)
        side_force = q * self.ref_area * 2.0 * np.radians(aoa_deg)
        
        # Moment = side_force * (CG - CP distance)
        # Note: This is very simplified but captures the physics of "Max Q * Alpha"
        return axial_g, side_force

if __name__ == "__main__":
    r = Rocket()
    print(f"Max m_dot: {r.m_dot_max:.2f} kg/s")
    print(f"Vac Thrust: {r.s1_vac_thrust/1e6:.2f} MN")
    print(f"Cd at M0.5: {r.get_cd(0.5):.3f}")
    print(f"Cd at M1.0: {r.get_cd(1.0):.3f}")
    print(f"Cd at M2.0: {r.get_cd(2.0):.3f}")
