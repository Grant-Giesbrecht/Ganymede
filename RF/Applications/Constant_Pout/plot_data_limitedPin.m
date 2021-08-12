% Data from 3053 4x100 12-Aug-2021 0858
Pin = [18.1, 15.4, 19.2, 18, 14.5];
mGamma = [.83, .63, .72, .61, .39];
aGamma = [304, 289, 262, 233, 183];
I = [];
V = [];
f = [];

Z_PAE_max_2Wdemo = complex(.797, 1.27)*50;
G_PAE_max_2Wdemo = (Z_PAE_max_2Wdemo - 50)/(Z_PAE_max_2Wdemo + 50);

Z_Gt_max_2Wdemo = complex(1.019, .867)*50;
G_Gt_max_2Wdemo = (Z_Gt_max_2Wdemo - 50)/(Z_Gt_max_2Wdemo + 50);

g = polcomplex(mGamma, aGamma, 'Unit', 'degrees');
g_rot = polcomplex(mGamma, aGamma+180, 'Unit', 'degrees');
% Z = V./I;

figure(4);
hold off;
smithplot(g, 'LineStyle', ':', 'Marker', '+')
hold on;
smithplot(g_rot, 'LineStyle', ':', 'Marker', '+')
smithplot(g_rot(3), 'Marker', 'o', 'MarkerSize', 10);
smithplot(g(3), 'Marker', 'o', 'MarkerSize', 8, 'EdgeColor', [0.4660 0.6740 0.1880]);
smithplot(G_PAE_max_2Wdemo, 'Marker', 'x', 'Color', [0, .7, 0])
smithplot(G_Gt_max_2Wdemo, 'Marker', 'x', 'Color', [.7, .2, .7])
legend('200mW Sweep', '200 mW Sweep, Rotated', '200 mW Sweep, Rotated, 10 GHz', '200mW Sweep, 10 GHz', '2W PAE Max', '2W G_{T} Max', 'Location', 'SouthWest')