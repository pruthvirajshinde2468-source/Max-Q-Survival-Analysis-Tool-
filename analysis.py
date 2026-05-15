import numpy as np

class Analysis:
    @staticmethod
    def get_summary(results, rocket_limits):
        """Extract key metrics from simulation results."""
        max_q_point = max(results, key=lambda x: x['q'])
        max_axial_g = max(results, key=lambda x: x['axial_g'])
        
        # Min safety margin for Q
        safety_margins_q = [(rocket_limits['q'] - r['q']) / rocket_limits['q'] for r in results]
        min_margin_q = min(safety_margins_q)
        
        # Burnout conditions
        burnout = results[-1]
        
        return {
            'max_q': max_q_point['q'],
            'max_q_alt': max_q_point['altitude'],
            'max_q_mach': max_q_point['mach'],
            'max_axial_g': max_axial_g['axial_g'],
            'min_margin_q': min_margin_q,
            'final_v': burnout['velocity'],
            'final_alt': burnout['altitude'],
            'final_t': burnout['time']
        }

    @staticmethod
    def calculate_penalties(baseline_summary, comparison_summary, isp_vac):
        """Calculate performance loss relative to baseline (usually Profile A)."""
        g0 = 9.80665
        dv_loss = baseline_summary['final_v'] - comparison_summary['final_v']
        
        # Estimate payload penalty using Rocket Equation sensitivity
        # m_final = m_initial * exp(-dv / ve)
        # dm_payload / m_final approx -dv_loss / ve
        ve = isp_vac * g0
        # For a 62t rocket, m_final is around 14t (dry + payload + stage 2)
        m_final_approx = 14000.0 
        payload_penalty = m_final_approx * (1 - np.exp(-dv_loss / ve))
        
        return {
            'dv_loss': dv_loss,
            'time_penalty': comparison_summary['final_t'] - baseline_summary['final_t'],
            'payload_penalty_kg': payload_penalty
        }

    @staticmethod
    def get_wind_comparison(results_calm, results_wind):
        """Compare Max-Q with and without wind."""
        max_q_calm = max(results_calm, key=lambda x: x['q'])['q']
        max_q_wind = max(results_wind, key=lambda x: x['q'])['q']
        
        # Max side load comparison
        max_side_calm = max(results_calm, key=lambda x: x['side_load'])['side_load']
        max_side_wind = max(results_wind, key=lambda x: x['side_load'])['side_load']
        
        return {
            'q_increase_pct': (max_q_wind - max_q_calm) / max_q_calm * 100,
            'side_load_increase_pct': (max_side_wind - max_side_calm) / max_side_calm * 100 if max_side_calm > 0 else 0
        }
