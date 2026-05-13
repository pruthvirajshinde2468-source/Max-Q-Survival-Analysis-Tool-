import numpy as np

class USStandardAtmosphere1976:
    """
    Implementation of the US Standard Atmosphere 1976 model.
    Reference: U.S. Standard Atmosphere, 1976, NOAA, NASA, USAF.
    """
    
    # Constants
    G0 = 9.80665  # Sea-level gravity (m/s^2)
    RE = 6356766.0  # Earth radius for geopotential calculation (m)
    R_GAS = 287.0528  # Gas constant for dry air (J/(kg*K))
    GAMMA = 1.4  # Ratio of specific heats for air
    
    # Layer definitions: (Geopotential Altitude h [m], Lapse Rate L [K/m], Temperature T [K], Pressure P [Pa])
    # h is the BASE of the layer.
    LAYERS = [
        (0.0, -0.0065, 288.15, 101325.0),    # Troposphere
        (11000.0, 0.0, 216.65, 22632.1),      # Tropopause
        (20000.0, 0.001, 216.65, 5474.89),    # Stratosphere 1
        (32000.0, 0.0028, 228.65, 868.019),   # Stratosphere 2
        (47000.0, 0.0, 270.65, 110.906),      # Stratopause
        (51000.0, -0.0028, 270.65, 66.9389),  # Mesosphere 1
        (71000.0, -0.002, 214.65, 3.95642),   # Mesosphere 2
        (84852.0, 0.0, 186.87, 0.3734)        # Mesopause / Thermosphere base
    ]

    @classmethod
    def get_geopotential_altitude(cls, z):
        """Convert geometric altitude (z) to geopotential altitude (h)."""
        return (cls.RE * z) / (cls.RE + z)

    @classmethod
    def get_properties(cls, z):
        """
        Calculate atmospheric properties at geometric altitude z (meters).
        Returns: (temperature [K], pressure [Pa], density [kg/m^3], speed_of_sound [m/s])
        """
        if z < 0:
            z = 0.0
            
        h = cls.get_geopotential_altitude(z)
        
        # Above 84.852 km (geopotential), the 1976 model changes significantly.
        # For Max-Q analysis (typically 10-15km), high accuracy above 86km is less critical,
        # but we'll use an exponential extrapolation for P/Rho if above mesosphere.
        
        # Find the appropriate layer
        base_h, L, base_T, base_P = cls.LAYERS[0]
        for i in range(len(cls.LAYERS)):
            if h < cls.LAYERS[i][0]:
                break
            base_h, L, base_T, base_P = cls.LAYERS[i]
            
        dh = h - base_h
        
        # Temperature
        T = base_T + L * dh
        
        # Pressure
        if L == 0:
            P = base_P * np.exp(-cls.G0 * dh / (cls.R_GAS * base_T))
        else:
            P = base_P * (T / base_T) ** (-cls.G0 / (L * cls.R_GAS))
            
        # Density
        rho = P / (cls.R_GAS * T)
        
        # Speed of sound
        if T > 0:
            a = np.sqrt(cls.GAMMA * cls.R_GAS * T)
        else:
            a = 0.0
            
        return T, P, rho, a

if __name__ == "__main__":
    # Quick test
    altitudes = [0, 11000, 20000, 50000, 80000, 120000]
    print(f"{'Alt(m)':>8} {'Temp(K)':>10} {'Press(Pa)':>10} {'Rho(kg/m3)':>10} {'Sound(m/s)':>10}")
    for z in altitudes:
        T, P, rho, a = USStandardAtmosphere1976.get_properties(z)
        print(f"{z:8.0f} {T:10.2f} {P:10.2e} {rho:10.2e} {a:10.2f}")
