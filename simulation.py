import numpy as np
from atmosphere import USStandardAtmosphere1976
from rocket import Rocket

class Simulation:
    def __init__(self, rocket):
        self.rocket = rocket
        self.dt = 0.1  # seconds
        
    def run(self, throttle_profile_func, wind_profile_func=None):
        """
        Runs a 2D trajectory simulation.
        throttle_profile_func: takes (time, altitude, velocity, mach) -> returns throttle (0-1)
        wind_profile_func: takes altitude -> returns horizontal wind speed (m/s)
        """
        # Initial conditions
        t = 0.0
        y = 0.0      # Altitude
        x = 0.0      # Downrange
        v = 0.01     # Velocity (non-zero for Mach calc)
        gamma = np.radians(90.0)  # Flight path angle (vertical start)
        prop_burned = 0.0
        
        results = []
        
        # Simulation loop - run until propellant is out or altitude reaches 150km
        while prop_burned < self.rocket.m_s1_prop and y < 150000 and y >= 0:
            # Atmosphere properties
            temp, p_amb, rho, a_sound = USStandardAtmosphere1976.get_properties(y)
            mach = v / a_sound
            
            # Wind effects
            v_wind = wind_profile_func(y) if wind_profile_func else 0.0
            # Relative velocity vector (v_rel_x, v_rel_y)
            # v_x = v * cos(gamma), v_y = v * sin(gamma)
            # v_rel_x = v_x - v_wind
            v_rel_x = v * np.cos(gamma) - v_wind
            v_rel_y = v * np.sin(gamma)
            v_rel = np.sqrt(v_rel_x**2 + v_rel_y**2)
            
            # Angle of Attack (alpha) - angle between rocket axis (assume follows gamma) and v_rel
            # Actually, the rocket axis usually follows the velocity vector v (not v_rel)
            # So alpha is the angle between the velocity vector and the relative velocity vector.
            alpha = np.abs(np.arctan2(v_rel_y, v_rel_x) - gamma)
            
            # Aerodynamics
            cd = self.rocket.get_cd(mach)
            q = 0.5 * rho * v_rel**2
            drag = q * cd * self.rocket.ref_area
            
            # Throttle and Propulsion
            throttle = throttle_profile_func(t, y, v, mach)
            thrust = self.rocket.get_thrust(y, throttle)
            m_dot = self.rocket.m_dot_max * throttle
            
            # Current Mass
            m = self.rocket.get_mass(prop_burned)
            
            # Gravity
            g = self.rocket.g0 * (self.rocket.RE / (self.rocket.RE + y))**2
            
            # Acceleration
            # v_dot = (Thrust - Drag*cos(alpha)) / m - g*sin(gamma)
            # This is simplified. Let's use components for better accuracy.
            
            # Thrust is along the rocket axis (gamma)
            fx = thrust * np.cos(gamma) - drag * (v_rel_x / v_rel)
            fy = thrust * np.sin(gamma) - drag * (v_rel_y / v_rel) - m * g
            
            ax = fx / m
            ay = fy / m
            
            # Update states
            x += v * np.cos(gamma) * self.dt
            y += v * np.sin(gamma) * self.dt
            
            # Update velocity components
            vx = v * np.cos(gamma) + ax * self.dt
            vy = v * np.sin(gamma) + ay * self.dt
            
            v = np.sqrt(vx**2 + vy**2)
            gamma = np.arctan2(vy, vx)
            
            # Gravity turn: kick over at 500m
            if y > 500 and t < 20:
                gamma -= np.radians(0.05) # Tiny pitch kick
            
            prop_burned += m_dot * self.dt
            t += self.dt
            
            # Structural Analysis
            accel_abs = np.sqrt(ax**2 + ay**2)
            axial_g, side_load = self.rocket.calculate_loads(q, v_rel, m, accel_abs, np.degrees(alpha))
            
            results.append({
                'time': t,
                'altitude': y,
                'velocity': v,
                'mach': mach,
                'q': q,
                'thrust': thrust,
                'mass': m,
                'gamma_deg': np.degrees(gamma),
                'alpha_deg': np.degrees(alpha),
                'axial_g': axial_g,
                'side_load': side_load,
                'throttle': throttle
            })
            
        return results

def get_profile_a(t, y, v, mach):
    return 1.0  # Full throttle

def get_profile_b(t, y, v, mach):
    if 0.8 <= mach <= 1.5:
        return 0.7
    return 1.0

def get_profile_c(t, y, v, mach):
    if 0.8 <= mach <= 1.5:
        return 0.5
    return 1.0

def constant_wind(y):
    # Simulated jet stream at 10-15km
    if 10000 <= y <= 15000:
        return 40.0 # 40 m/s wind
    return 0.0

if __name__ == "__main__":
    r = Rocket()
    sim = Simulation(r)
    res = sim.run(get_profile_a)
    
    # Find Max-Q
    max_q_data = max(res, key=lambda x: x['q'])
    print(f"Max-Q: {max_q_data['q']:.0f} Pa at {max_q_data['altitude']/1000:.2f} km")
