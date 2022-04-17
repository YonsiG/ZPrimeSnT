from curses import can_change_color
from hashlib import new
from numbers import Integral
from tkinter.tix import Tree
import ROOT
import copy
import argparse
import os
from datetime import date    

user = os.environ.get("USER")
today= date.today().strftime("%b-%d-%Y")

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--inDir", default="./cpp/temp_data/", help="Choose input directory. Default: './cpp/temp_data/'.")
parser.add_argument("--outDir", default="/home/users/"+os.environ.get("USER")+"/public_html/Zprime/plots_"+today, help="Choose output directory. Default: '/home/users/"+user+"/public_html/Zprime/pots_"+today+"'.")
parser.add_argument("--data", action="store_true", default=False, help="Include data")
parser.add_argument("--signalMass", default=[], action="append", help="Signal masspoints to plot. Default: All.")
parser.add_argument("--signalScale", default=1.0, help="Number to scale the signal by.")
args = parser.parse_args()

args.inDir = args.inDir.rstrip("/")+"/"
args.outDir = args.outDir.rstrip("/")+"/"

if not os.path.exists(args.outDir):
    os.makedirs(args.outDir)
os.system('cp '+args.inDir+'../../utils/index.php '+args.outDir)

if len(args.signalMass)==0: 
    args.signalMass = [200,400,700,1000,1500,2000]
signalXSecScale = { "200": 1.0, "400": 50, "700": 25.0, "1000": 80.0, "1500": 450.0, "2000": 2000.0}

def get_plot(plotFile, plotname, fillColor=None, lineColor=None, lineWidth=0):
    plot = plotFile.Get(plotname)

    plot.SetBinContent(1, plot.GetBinContent(1) + plot.GetBinContent(0))
    plot.SetBinContent(plot.GetNbinsX(), plot.GetBinContent(plot.GetNbinsX() + 1) + plot.GetBinContent(plot.GetNbinsX()))

    if fillColor: 
        plot.SetFillColor(fillColor)
    if lineColor: 
        plot.SetLineColor(lineColor)
    plot.SetLineWidth(lineWidth)
    #plot.Sumw2()

    return plot

def draw_plot(plotname="fatjet_msoftdrop", title="myTitle", log=True, compare_data=False, DoRatio=True):
    #open file
    signalfiles = []
    ZToMuMufiles = []
    for mass in args.signalMass: 
        signalfiles.append(ROOT.TFile(args.inDir+"output_Y3_M"+str(mass)+"_2018.root"))
    for m1,m2 in zip(["50","120","200","400","800","1400","2300","3500","4500","6000"],["120","200","400","800","1400","2300","3500","4500","6000","Inf"]): 
        ZToMuMufiles.append(ROOT.TFile(args.inDir+"output_ZToMuMu_"+m1+"_"+m2+"_2018.root"))
    #DYfile =     ROOT.TFile(args.inDir+"output_DY_2018.root")
    WWfile =     ROOT.TFile(args.inDir+"output_WW_2018.root")
    WZfile =     ROOT.TFile(args.inDir+"output_WZ_2018.root")
    ZZfile =     ROOT.TFile(args.inDir+"output_ZZ_2018.root")
    ttbarfile =  ROOT.TFile(args.inDir+"output_ttbar_2018.root")
    tWfile =     ROOT.TFile(args.inDir+"output_tW_2018.root")
    tbarWfile =  ROOT.TFile(args.inDir+"output_tbarW_2018.root")
    TTWfile =    ROOT.TFile(args.inDir+"output_TTW_2018.root")
    TTZfile =    ROOT.TFile(args.inDir+"output_TTZ_2018.root")
    TTHNobbfile= ROOT.TFile(args.inDir+"output_TTHToNonbb_2018.root")
    #TTHbbfile =  ROOT.TFile(args.inDir+"output_TTHTobb_2018.root")
    if compare_data: 
        datafile = ROOT.TFile(args.inDir+"data_2018_2_selected.root")

    #get historam
    signalplots = []
    ZToMuMuplots = []
    for i in range(len(args.signalMass)): 
        signalplots.append(get_plot(signalfiles[i],plotname,lineColor=ROOT.kPink+i,lineWidth=2))
    for i in range(len(ZToMuMufiles)): 
        ZToMuMuplots.append(get_plot(ZToMuMufiles[i],plotname,fillColor=ROOT.kOrange))
    if compare_data: dataplot = get_plot(datafile,plotname,lineColor=ROOT.kBlack,lineWidth=2)
    #DYplot = get_plot(DYfile,plotname,fillColor=ROOT.kOrange)
    WWplot = get_plot(WWfile,plotname,fillColor=ROOT.kOrange+1)
    WZplot = get_plot(WZfile,plotname,fillColor=ROOT.kOrange+2)
    ZZplot = get_plot(ZZfile,plotname,fillColor=ROOT.kOrange+3)
    ttbarplot = get_plot(ttbarfile,plotname,fillColor=ROOT.kOrange+4)
    tWplot = get_plot(tWfile,plotname,fillColor=ROOT.kOrange+5)
    tbarWplot = get_plot(tbarWfile,plotname,fillColor=ROOT.kOrange+5)
    TTWplot = get_plot(TTWfile,plotname,fillColor=ROOT.kOrange+6)
    TTZplot = get_plot(TTZfile,plotname,fillColor=ROOT.kOrange+6)
    TTHNobbplot = get_plot(TTHNobbfile,plotname,fillColor=ROOT.kOrange+6)
   #TTHbbplot = TTHbbfile.Get(plotname)

    #add histos
    ZToMuMuplot = ZToMuMuplots[0].Clone("ZToMuMu")
    for i in range(1,len(ZToMuMuplots)): ZToMuMuplot.Add(ZToMuMuplots[i])
    ST_tWplot = tWplot.Clone("ST_tW")
    ST_tWplot.Add(tbarWplot)
    TTXplot = TTWplot.Clone("TTX")
    TTXplot.Add(TTZplot)
    TTXplot.Add(TTHNobbplot)

    #build stack
    stack = ROOT.THStack("stack","")
    stack.Add(ZZplot)
    stack.Add(WZplot)
    stack.Add(WWplot)
    stack.Add(TTXplot)
    #stack.Add(TTWplot)
    #stack.Add(TTZplot)
    #stack.Add(TTHNobbplot)
    #stack.Add(TTHbbplot)
    stack.Add(ST_tWplot)
    #stack.Add(tWplot)
    #stack.Add(tbarWplot)
    stack.Add(ttbarplot)
    stack.Add(ZToMuMuplot)
    #stack.Add(DYplot)
    stack.SetTitle(title)

    #plot legends, ranges
    legend = ROOT.TLegend(0.65,0.65,0.97,0.97)
    legend.SetTextFont(60)
    legend.SetTextSize(0.02)

    for i,mass in enumerate(args.signalMass): 
        if log==False and args.signalScale:
            legend.AddEntry(signalplots[i],"Y3_M"+str(mass)+" %1.2E x%1.1E"%(signalplots[i].Integral(0,-1),(float(args.signalScale))*(float(signalXSecScale[str(mass)]))))
        else:
            legend.AddEntry(signalplots[i],"Y3_M"+str(mass)+" %1.2E"%(signalplots[i].Integral(0,-1)))
            
    if compare_data: 
        legend.AddEntry(dataplot,"data %1.2E"%(dataplot.Integral(0,-1)))
    legend.AddEntry(ZToMuMuplot, "ZToMuMu %1.2E"%(ZToMuMuplot.Integral(0,-1)))
    #legend.AddEntry(DYplot, "DY %1.2E"%(DYplot.Integral(0,-1)))
    legend.AddEntry(ttbarplot,"ttbar %1.2E"%(ttbarplot.Integral(0,-1)))
    legend.AddEntry(tWplot,"tW+tbarW %1.2E"%(ST_tWplot.Integral(0,-1)))
    #legend.AddEntry(tWplot,"tW %1.2E"%(tWplot.Integral(0,-1)))
    #legend.AddEntry(tbarWplot,"tbarW %1.2E"%(tbarWplot.Integral(0,-1)))
    legend.AddEntry(TTXplot,"ttX %1.2E"%(TTXplot.Integral(0,-1)))
    #legend.AddEntry(TTWplot,"ttW %1.2E"%(TTWplot.Integral(0,-1)))
    #legend.AddEntry(TTZplot,"ttZ %1.2E"%(TTZplot.Integral(0,-1)))
    #legend.AddEntry(TTHNobbplot,"ttHNobb %1.2E"%(TTHNobbplot.Integral(0,-1)))
    #legend.AddEntry(TTHbbplot,"ttHbb %1.2E"%(TTHbbplot.Integral(0,-1))) 
    legend.AddEntry(WWplot, "WW %1.2E"%(WWplot.Integral(0,-1)))
    legend.AddEntry(WZplot, "WZ %1.2E"%(WZplot.Integral(0,-1)))
    legend.AddEntry(ZZplot,"ZZ %1.2E"%(ZZplot.Integral(0,-1)))

    #define canvas
    canvas = ROOT.TCanvas("canvas","canvas",800,800)

    if DoRatio==True:
        #MCplot = copy.deepcopy(DYplot)
        MCplot = copy.deepcopy(ZToMuMuplot)
        MCplot.Add(WWplot)
        MCplot.Add(WZplot)
        MCplot.Add(ZZplot)
        MCplot.Add(ttbarplot)
        MCplot.Add(tWplot)
        MCplot.Add(TTXplot)
        ratioplot=copy.deepcopy(dataplot)
        ratioplot.Divide(MCplot)
        ratioplot.SetTitle(";"+title+";data / MC")
        pad1 = ROOT.TPad("pad1","pad1",0,0.3,1,1)
        pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.3)
        pad1.Draw()
        pad2.Draw()
        pad2.cd()
        ratioplot.Draw("E0")

    if DoRatio==False:
        pad1 = ROOT.TPad("pad1","pad1",0,0,1,1)
        pad1.Draw()

    pad1.cd()
    if log==True:
        pad1.SetLogy()
        #ROOT.gPad.SetLogy(1)

    #plot data,stack, signal, data  
    stack.Draw("HIST")
    histMax = 0.0
    for i,mass in enumerate(args.signalMass):
        if log==False:
            if args.signalScale: 
                signalplots[i].Scale((float(args.signalScale))*(float(signalXSecScale[str(mass)])))
        if histMax < signalplots[i].GetMaximum(): 
            histMax = signalplots[i].GetMaximum()
        signalplots[i].Draw("HIST same")
    if compare_data: dataplot.Draw("E0 same")

    if histMax < stack.GetMaximum(): histMax = stack.GetMaximum()
    stack.SetMaximum(1.1*histMax)
    if log==True:
        stack.SetMinimum(10e-2)
        #stack.Draw("Hist")

    legend.Draw()

    #print and save
    if log==True:
        if compare_data==False:
            canvas.SaveAs(args.outDir + plotname + "_s+b_log.png")
        if compare_data==True:
            canvas.SaveAs(args.outDir + plotname + "_mc+data_log.png")
    if log==False:
        if compare_data==False:
            canvas.SaveAs(args.outDir + plotname + "_s+b_linear.png")
        if compare_data==True:
            canvas.SaveAs(args.outDir + plotname + "_mc+data_linear.png")

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

listofplots = []
listfile = ROOT.TFile(args.inDir+"output_ttbar_2018.root")
listkeys = listfile.GetListOfKeys()
size = listkeys.GetSize()
for i in range(0,size):
    listofplots.append(listkeys.At(i).GetName())
toexclude = []

for plot in listofplots:
    if plot in toexclude:
        continue
    title=plot
    draw_plot(plot, title, False, args.data, False)
    draw_plot(plot, title, True , args.data, False)
