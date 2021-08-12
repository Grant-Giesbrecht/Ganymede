% Data from 3053 4x100 12-Aug-2021 0858
Pin = [17.9, 27.4, 24.5, 14.6, 22.8];
mGamma = [.77, .85, .79, .37, .99];
aGamma = [168, 274, 220, 238, 90];
I = [.167, .222, .208, .118, .113];
V = [20, 19.99, 19.99, 20, 20];
f = [8e9, 9e9, 10e9, 11e9, 12e9];

g = polcomplex(mGamma, aGamma, 'Unit', 'degrees');
Z = V./I;

figure(4);
smithplot(g, 'LineStyle', ':', 'Marker', '+')