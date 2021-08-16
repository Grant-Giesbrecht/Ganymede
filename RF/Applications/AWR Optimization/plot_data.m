% Load data
filename = "scan_3053_4x100_16-Aug-2021 1158.ddf";
ddf = DDFIO;
ddf.load(filename);

% Check data read successful
if ddf.numVar() < 4
	displ("Missing variables. Aborting!");
	return
end

ddf.show()
argGamma = ddf.get('_ArgGamma');
magGamma = ddf.get('_MagGamma');
I = ddf.get("SweepSchema_3053_4x100_AP_HB__Icomp_DCVS_VDS_0__").val;
V = ddf.get("SweepSchema_3053_4x100_AP_HB__Vcomp_DCVS_VDS_0__").val;
PAE = ddf.get("SweepSchema_3053_4x100_AP_HB_PAE_PORT_1_PORT_2_").val;
f = ddf.get("freq").val;

G = polcomplex(magGamma.val, argGamma.val);
Z_vi = V./I;

figure(4)
hold off
smithplot(G, 'LineStyle', ':', 'Marker', '+')

% figure(5);
% hold off
% plot(f, Z_vi);
% hold on;
% plot(f, G2Z(G, 50));