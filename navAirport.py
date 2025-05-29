class NavAirport:
    def __init__(self, name, sids=None, stars=None):
        self.name = name
        self.sids = sids if sids is not None else []
        self.stars = stars if stars is not None else []


def add_sid(navairport, navpoint_number):
    if navpoint_number not in navairport.sids:
        navairport.sids.append(navpoint_number)
        
def add_star(navairport, navpoint_number):
    if navpoint_number not in navairport.stars:
        navairport.stars.append(navpoint_number)
        
def navairport_to_str(navairport):
    return f"Aeropuerto: {navairport.name}, SIDs: {len(navairport.sids)}, STARs: {len(navairport.stars)}"
    
def get_sids(navairport):
    return navairport.sids
    
def get_stars(navairport):
    return navairport.stars
