import math
import random
import os

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import (
    Rectangle, Color, Triangle, Ellipse,
    Line, RoundedRectangle
)
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.storage.jsonstore import JsonStore

store = JsonStore('gravity_switch_score.json')

W = Window.width
H = Window.height

SOL_H     = 30
PLAFOND_H = 30
TAILLE_J  = 30
RAYON_HIT = 9

PALIERS = [
    (0,  "EASY",     "00FF88"),
    (8,  "MEDIUM",   "FFD700"),
    (18, "HARD",     "FF6B00"),
    (30, "EXTREME",  "FF2255"),
    (45, "INSANE",   "CC00FF"),
    (65, "GOD MODE", "FF00FF"),
]

MSG_RECORD = ["NEW RECORD!", "UNBELIEVABLE!", "YOU'RE ON FIRE!", "LEGENDARY!"]
MSG_HALF   = ["SO CLOSE...",  "ALMOST THERE!", "DON'T GIVE UP!", "KEEP PUSHING!"]
MSG_LOW    = ["TRY AGAIN",    "YOU GOT THIS",  "KEEP GOING",     "ONE MORE RUN!"]


def get_palier(score):
    nom, couleur = PALIERS[0][1], PALIERS[0][2]
    for seuil, n, c in PALIERS:
        if score >= seuil:
            nom, couleur = n, c
    return nom, couleur


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


# ─── Particule ────────────────────────────────────────────────
class Particule:
    def __init__(self, canvas, x, y, couleur):
        self.canvas = canvas
        self.x = x; self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(1, 9)
        self.vie = 1.0
        self.taille = random.uniform(4, 12)
        r, g, b = hex_to_rgb(couleur)
        self.ci = self.ei = None
        with self.canvas:
            self.ci = Color(r, g, b, 1.0)
            self.ei = Ellipse(
                pos=(self.x - self.taille/2, self.y - self.taille/2),
                size=(self.taille, self.taille))

    def update(self, dt):
        self.vie -= dt * 2.0
        self.vy  -= 0.18
        self.x   += self.vx
        self.y   += self.vy
        if self.ci: self.ci.a = max(0, self.vie)
        if self.ei: self.ei.pos = (self.x - self.taille/2, self.y - self.taille/2)
        return self.vie > 0

    def kill(self):
        try: self.canvas.remove(self.ci)
        except Exception: pass
        try: self.canvas.remove(self.ei)
        except Exception: pass


# ─── Trail ────────────────────────────────────────────────────
class Trail:
    MAX = 12

    def __init__(self, canvas):
        self.canvas = canvas
        self.pts = []
        self.instrs = []
        with self.canvas:
            for _ in range(self.MAX):
                c = Color(0, 1, 1, 0)
                e = Ellipse(pos=(0, 0), size=(8, 8))
                self.instrs.append((c, e))

    def add(self, x, y):
        self.pts.insert(0, [x, y, 1.0])
        if len(self.pts) > self.MAX: self.pts.pop()

    def update(self):
        for i, (c, e) in enumerate(self.instrs):
            if i < len(self.pts):
                px, py, a = self.pts[i]
                self.pts[i][2] = max(0, a - 0.10)
                c.a = self.pts[i][2]
                c.r, c.g, c.b = 0, 1, 1
                sz = max(1, 9 - i * 0.7)
                e.pos  = (px + TAILLE_J/2 - sz/2, py + TAILLE_J/2 - sz/2)
                e.size = (sz, sz)
            else:
                c.a = 0

    def clear(self):
        self.pts = []
        for c, e in self.instrs: c.a = 0


# ─── Étoile ───────────────────────────────────────────────────
class Etoile:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = random.uniform(0, W)
        self.y = random.uniform(0, H)
        self.r = random.uniform(0.6, 2.2)
        self.vy = random.uniform(0.2, 1.0)
        self.alpha = random.uniform(0.2, 0.9)
        self.ci = self.ri = None
        with self.canvas:
            self.ci = Color(1, 1, 1, self.alpha)
            self.ri = Ellipse(pos=(self.x, self.y), size=(self.r*2, self.r*2))

    def update(self, dt):
        self.y -= self.vy
        if self.ci: self.ci.a = self.alpha
        if self.ri: self.ri.pos = (self.x, self.y)
        if self.y < -5:
            self.x = random.uniform(0, W)
            self.y = H + 5
            self.alpha = random.uniform(0.2, 0.9)

    def kill(self):
        try: self.canvas.remove(self.ci)
        except Exception: pass
        try: self.canvas.remove(self.ri)
        except Exception: pass


# ════════════════════════════════════════════════════════════════
class Joueur(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state  = "loading"
        self.score       = 0
        self.last_score  = 0
        self.pics        = []
        self.particules  = []
        self.etoiles     = []
        self.loading_pct = 0.0
        self.flash_alpha = 0.0
        self._pf_alpha = 0.0   # palier flash
        self._pf_r = self._pf_g = self._pf_b = 1.0

        self.update_event = self.pic_event = None
        self.diff_event   = self.score_event = None
        self.menu_event   = None

        base = os.path.dirname(os.path.abspath(__file__))
        self.snd_start    = SoundLoader.load(os.path.join(base, "start.mp3"))
        self.snd_playing  = SoundLoader.load(os.path.join(base, "playing.mp3"))
        self.snd_gameover = SoundLoader.load(os.path.join(base, "gameover.mp3"))

        with self.canvas:
            Color(0.03, 0, 0.09, 1)
            Rectangle(pos=(0,0), size=(W,H))
            Color(0.055, 0.025, 0.12, 1)
            for gy in range(0, int(H), 55):
                Line(points=[0, gy, W, gy], width=0.6)
            Color(1, 0.12, 0.12, 1)
            self.sol     = Rectangle(pos=(0,0),           size=(W, SOL_H))
            self.plafond = Rectangle(pos=(0,H-PLAFOND_H), size=(W, PLAFOND_H))
            Color(1, 0.08, 0.08, 0.13)
            Rectangle(pos=(0, SOL_H),              size=(W, 14))
            Rectangle(pos=(0, H-PLAFOND_H-14),     size=(W, 14))
            Color(0, 1, 1, 1)
            self.rect = Rectangle(size=(TAILLE_J, TAILLE_J))
            self.flash_ci = Color(1, 0.2, 0.1, 0)
            self.flash_ri = Rectangle(pos=(0,0), size=(W,H))

        self.trail = Trail(self.canvas)
        self._build_labels()
        self._build_bouton()
        self._build_loading()

        best = store.get('best')['score'] if store.exists('best') else 0
        self.best_score  = best
        self.pos_x = 100; self.pos_y = H/2
        self.vitesse = 0; self.gravite = -0.8; self.vitesse_jeu = 5
        self.rect.pos = (-999, -999)
        Clock.schedule_interval(self._update_loading, 1/60)

    # ── BUILD LABELS ──────────────────────────────────────────
    # Positions FIXES depuis le haut, taille = (W, h),
    # pos = (0, y) → aucun chevauchement possible.
    #
    # MENU / GAMEOVER :
    #  H-230 → Titre (210px)
    #  H-310 → 👑 best (55px)
    #  H-388 → ◉ last  (56px)
    #  H-458 → GAME OVER (56px)   — gameover only
    #  H-520 → message             — gameover only
    #  H-558 → palier              — gameover only
    #
    # HUD :
    #  H-100 → score (65px)
    #  H-130 → 👑 best (28px)
    #  H-156 → palier (24px)
    # ──────────────────────────────────────────────────────────
    def _build_labels(self):
        def lbl(text, fsize, bold, y, h, color, op=0, markup=False):
            return Label(text=text, font_size=fsize, bold=bold,
                         halign='center', size=(W, h), pos=(0, y),
                         color=color, opacity=op, markup=markup)

        self.lbl_titre = lbl(
            "GRAVITY\nSWITCH", '46sp', True,
            H-230, 210, (0,1,1,1))

        self.lbl_crown = lbl(
            f"👑  {self.best_score if hasattr(self,'best_score') else 0}",
            '28sp', True, H-310, 55, (1,0.85,0,1))

        self.lbl_last = lbl(
            "◉  0", '30sp', True,
            H-388, 56, (0.75,0.75,1,1))

        self.lbl_go = lbl(
            "GAME OVER", '30sp', True,
            H-458, 56, (1,0.22,0.12,1))

        self.lbl_msg = lbl(
            "", '20sp', True,
            H-520, 42, (1,1,0,1))

        self.lbl_go_palier = lbl(
            "", '16sp', True,
            H-558, 34, (0,1,0.53,1))

        # HUD
        self.lbl_hud_score = lbl(
            "0", '40sp', True,
            H-100, 65, (1,1,1,1))

        self.lbl_hud_best = lbl(
            "👑  0", '15sp', False,
            H-130, 28, (1,0.85,0,0.9))

        self.lbl_hud_palier = lbl(
            "", '12sp', True,
            H-156, 24, (0,1,0.53,1))

        # Flash palier (centre)
        self.lbl_pf = lbl(
            "", '22sp', True,
            H/2+50, 46, (1,1,1,0))
        self.lbl_pf.opacity = 1   # opacity!=color[3], couleur gère le alpha

        for l in [self.lbl_titre, self.lbl_crown, self.lbl_last,
                  self.lbl_go, self.lbl_msg, self.lbl_go_palier,
                  self.lbl_hud_score, self.lbl_hud_best, self.lbl_hud_palier,
                  self.lbl_pf]:
            self.add_widget(l)

    def _build_bouton(self):
        self.btn = Button(
            size_hint=(None,None), size=(130,130),
            pos=(W/2-65, 72),
            background_color=(0,0,0,0), opacity=0)
        self.btn.bind(on_press=self._on_btn)
        self.add_widget(self.btn)
        with self.btn.canvas.before:
            Color(0.07, 0.03, 0.16, 1)
            RoundedRectangle(size=(130,130), pos=self.btn.pos, radius=[65])
            Color(0, 1, 1, 1)
            Line(circle=(self.btn.x+65, self.btn.y+65, 60), width=2.8)
        self.btn_icon = Label(
            text="▶", font_size='52sp', color=(0,1,1,1),
            pos_hint={'center_x':.5,'center_y':.5})
        self.btn.add_widget(self.btn_icon)

    def _build_loading(self):
        with self.canvas.after:
            self.ld_bg_ci   = Color(0.03, 0, 0.09, 1)
            self.ld_bg_ri   = Rectangle(pos=(0,0), size=(W,H))
            Color(0.10, 0.05, 0.22, 1)
            RoundedRectangle(pos=(W/2-140, H/2-12), size=(280,14), radius=[7])
            self.ld_fill_ci = Color(0, 1, 1, 1)
            self.ld_fill_ri = RoundedRectangle(pos=(W/2-140, H/2-12), size=(0,14), radius=[7])
            self.ld_glow_ci = Color(0, 1, 1, 0.18)
            self.ld_glow_ri = RoundedRectangle(pos=(W/2-140, H/2-18), size=(0,26), radius=[13])
        self.lbl_ld_title = Label(
            text="GRAVITY SWITCH", font_size='30sp', bold=True,
            halign='center', pos=(W/2-185, H/2+55), size=(370,65),
            color=(0,1,1,1))
        self.lbl_ld_pct = Label(
            text="0%", font_size='14sp', halign='center',
            pos=(W/2-55, H/2-38), size=(110,28), color=(0.55,0.88,1,1))
        self.lbl_ld_sub = Label(
            text="by GravityLab", font_size='12sp', halign='center',
            pos=(W/2-100, H/2-66), size=(200,26), color=(0.35,0.35,0.55,1))
        for l in [self.lbl_ld_title, self.lbl_ld_pct, self.lbl_ld_sub]:
            self.add_widget(l)

    # ── HELPERS ───────────────────────────────────────────────
    def _hide_all(self):
        for l in [self.lbl_titre, self.lbl_crown, self.lbl_last,
                  self.lbl_go, self.lbl_msg, self.lbl_go_palier,
                  self.lbl_hud_score, self.lbl_hud_best, self.lbl_hud_palier]:
            l.opacity = 0
        self.btn.opacity = 0

    def _show_menu(self, gameover=False):
        self._hide_all()
        self.lbl_titre.opacity = 1
        self.lbl_crown.opacity = 1
        self.lbl_last.opacity  = 1
        if gameover:
            self.lbl_go.opacity        = 1
            self.lbl_msg.opacity       = 1
            self.lbl_go_palier.opacity = 1
            self.btn_icon.text = "⟳"
        else:
            self.btn_icon.text = "▶"
        self.btn_icon.color = (0,1,1,1)
        self.btn.opacity    = 1

    def _show_hud(self):
        self._hide_all()
        self.lbl_hud_score.opacity  = 1
        self.lbl_hud_best.opacity   = 1
        self.lbl_hud_palier.opacity = 1

    # ── LOADING ───────────────────────────────────────────────
    def _update_loading(self, dt):
        self.loading_pct = min(100, self.loading_pct + random.uniform(0.7,2.0))
        p = self.loading_pct/100
        self.ld_fill_ri.size = (280*p, 14)
        self.ld_glow_ri.size = (280*p, 26)
        self.lbl_ld_pct.text = f"{int(self.loading_pct)}%"
        if self.loading_pct >= 100:
            Clock.unschedule(self._update_loading)
            Clock.schedule_once(self._fade_loading, 0.35)

    def _fade_loading(self, *_):
        self._fade_step = 0.0
        def step(dt):
            self._fade_step += 0.045
            a = max(0.0, 1.0-self._fade_step)
            self.ld_bg_ci.a           = a
            self.ld_fill_ci.a         = a
            self.ld_glow_ci.a         = a*0.18
            self.lbl_ld_title.opacity = a
            self.lbl_ld_pct.opacity   = a
            self.lbl_ld_sub.opacity   = a
            if a <= 0:
                Clock.unschedule(step)
                self._enter_menu()
        Clock.schedule_interval(step, 1/60)

    # ── MENU ──────────────────────────────────────────────────
    def _enter_menu(self):
        self.game_state = "menu"
        self.rect.pos = (-999,-999)
        best = store.get('best')['score'] if store.exists('best') else 0
        self.best_score = best
        self.lbl_crown.text = f"👑  {self.best_score}"
        self.lbl_last.text  = f"◉  {self.last_score}"
        self._show_menu(gameover=False)
        self._start_etoiles()

    def _start_etoiles(self):
        with self.canvas:
            for _ in range(60):
                self.etoiles.append(Etoile(self.canvas))
        self.menu_event = Clock.schedule_interval(self._update_menu, 1/60)

    def _update_menu(self, dt):
        for e in self.etoiles: e.update(dt)
        t = Clock.get_boottime()
        g = 0.68 + 0.32*math.sin(t*2.2)
        self.lbl_titre.color = (0, g, 1, 1)

    def _stop_etoiles(self):
        if self.menu_event:
            self.menu_event.cancel()
            self.menu_event = None
        for e in self.etoiles: e.kill()
        self.etoiles = []

    # ── BOUTON ────────────────────────────────────────────────
    def _on_btn(self, *_):
        if self.game_state in ("menu","gameover"):
            self._stop_etoiles()
            self._hide_all()
            self._lancer()

    # ── LANCEMENT ─────────────────────────────────────────────
    def _lancer(self):
        self._reset()
        self.game_state = "playing"
        self._show_hud()
        self.lbl_hud_score.text   = "0"
        self.lbl_hud_best.text    = f"👑  {self.best_score}"
        self.lbl_hud_palier.text  = "◆ EASY ◆"
        self.lbl_hud_palier.color = (0,1,0.53,1)
        if self.snd_playing:
            self.snd_playing.loop = True
            self.snd_playing.play()
        if self.snd_start: self.snd_start.play()
        self.update_event = Clock.schedule_interval(self.update,     1/60)
        self.pic_event    = Clock.schedule_interval(self.creer_pic,  0.30)
        self.diff_event   = Clock.schedule_interval(self._augm_diff, 2.5)
        self.score_event  = Clock.schedule_interval(self._add_score, 1.0)

    def _reset(self):
        self._stop_clocks()
        self.pos_x = 100; self.pos_y = H/2
        self.vitesse = 0; self.gravite = -0.8
        self.score = 0; self.vitesse_jeu = 5
        self.flash_alpha = 0.0; self.flash_ci.a = 0
        self._pf_alpha = 0.0
        self.rect.pos = (self.pos_x, self.pos_y)
        self.trail.clear()
        for pic in self.pics:
            try: self.canvas.remove(pic[0])
            except Exception: pass
        self.pics = []
        for p in self.particules: p.kill()
        self.particules = []

    def _stop_clocks(self):
        for ev in [self.update_event, self.pic_event,
                   self.diff_event, self.score_event]:
            if ev: ev.cancel()
        self.update_event = self.pic_event = \
            self.diff_event = self.score_event = None
        if self.snd_playing: self.snd_playing.stop()

    # ── SCORE ─────────────────────────────────────────────────
    def _add_score(self, dt):
        if self.game_state != "playing": return
        self.score += 1
        self.lbl_hud_score.text = str(self.score)
        if self.score > self.best_score:
            self.best_score = self.score
            store.put('best', score=self.best_score)
            self.lbl_hud_best.text = f"👑  {self.best_score}"
        nom, coul = get_palier(self.score)
        r,g,b = hex_to_rgb(coul)
        self.lbl_hud_palier.text  = f"◆ {nom} ◆"
        self.lbl_hud_palier.color = (r,g,b,1)
        seuils = [s for s,_,_ in PALIERS]
        if self.score in seuils and self.score > 0:
            nom2, c2 = get_palier(self.score)
            r2,g2,b2 = hex_to_rgb(c2)
            self._pf_r=r2; self._pf_g=g2; self._pf_b=b2
            self._pf_alpha = 1.0
            self.lbl_pf.text = f"▲ {nom2}!"

    def _augm_diff(self, dt):
        if self.game_state == "playing":
            self.vitesse_jeu = min(self.vitesse_jeu+0.55, 14.0)

    # ── PICS ──────────────────────────────────────────────────
    def creer_pic(self, dt):
        if self.game_state != "playing": return
        t = random.randint(50,100)
        y = random.randint(SOL_H+10, int(H-PLAFOND_H-15-t))
        x = W
        r = random.uniform(0.3,1.0)
        g = random.uniform(0.1,0.6)
        with self.canvas:
            Color(r, g, 1.0, 1)
            tri = Triangle(points=[x+t,y, x+t,y+t, x,y+t/2])
        self.pics.append([tri, x, y, t])

    # ── COLLISION ─────────────────────────────────────────────
    def _pt_in_tri(self, px,py, ax,ay, bx,by, cx,cy):
        def s(x1,y1,x2,y2,x3,y3):
            return (x1-x3)*(y2-y3)-(x2-x3)*(y1-y3)
        d1=s(px,py,ax,ay,bx,by)
        d2=s(px,py,bx,by,cx,cy)
        d3=s(px,py,cx,cy,ax,ay)
        return not ((d1<0 or d2<0 or d3<0) and (d1>0 or d2>0 or d3>0))

    # ── UPDATE ────────────────────────────────────────────────
    def update(self, dt):
        if self.game_state != "playing": return

        self.vitesse += self.gravite
        self.pos_y   += self.vitesse

        if self.pos_y <= SOL_H:
            self.pos_y = SOL_H
            self.rect.pos = (self.pos_x, self.pos_y)
            self.mourir(); return
        if self.pos_y + TAILLE_J >= H-PLAFOND_H:
            self.pos_y = H-PLAFOND_H-TAILLE_J
            self.rect.pos = (self.pos_x, self.pos_y)
            self.mourir(); return

        self.rect.pos = (self.pos_x, self.pos_y)
        self.trail.add(self.pos_x, self.pos_y)
        self.trail.update()

        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha-0.045)
            self.flash_ci.a  = self.flash_alpha

        if self._pf_alpha > 0:
            self._pf_alpha = max(0, self._pf_alpha-0.007)
            self.lbl_pf.color = (self._pf_r, self._pf_g, self._pf_b, self._pf_alpha)

        jcx = self.pos_x+15; jcy = self.pos_y+15

        for pic in self.pics[:]:
            pic[1] -= self.vitesse_jeu
            t  = pic[3]
            ax = pic[1]+t; ay = pic[2]
            bx = pic[1]+t; by = pic[2]+t
            cx = pic[1];   cy = pic[2]+t/2
            pic[0].points = [ax,ay, bx,by, cx,cy]
            if pic[1] < -t:
                self.canvas.remove(pic[0])
                self.pics.remove(pic)
                continue
            hit = False
            for i in range(8):
                ang = math.radians(i*45)
                if self._pt_in_tri(
                    jcx+RAYON_HIT*math.cos(ang),
                    jcy+RAYON_HIT*math.sin(ang),
                    ax,ay, bx,by, cx,cy):
                    hit = True; break
            if not hit and self._pt_in_tri(jcx,jcy, ax,ay, bx,by, cx,cy):
                hit = True
            if hit:
                self.mourir(); return

        for p in self.particules[:]:
            if not p.update(dt):
                p.kill()
                self.particules.remove(p)

    # ── MORT ──────────────────────────────────────────────────
    def mourir(self):
        if self.game_state != "playing": return
        self.game_state = "gameover"

        is_record = (self.score > 0 and self.score >= self.best_score)
        self.last_score = self.score

        if self.snd_playing:  self.snd_playing.stop()
        if self.snd_gameover: self.snd_gameover.play()

        self.flash_alpha = 0.85; self.flash_ci.a = 0.85

        # Explosion
        cx = self.pos_x+15; cy = self.pos_y+15
        for _ in range(35):
            col = random.choice(["FF4444","FF8800","FFDD00","FF2266","FF66FF"])
            self.particules.append(Particule(self.canvas, cx, cy, col))

        # Cacher joueur + trail
        self.rect.pos = (-999,-999)
        self.trail.clear()

        # ── Effacer TOUS les pics ─────────────────────────────
        for pic in self.pics:
            try: self.canvas.remove(pic[0])
            except Exception: pass
        self.pics = []

        self._stop_clocks()

        # Message selon performance
        nom, coul = get_palier(self.score)
        r,g,b = hex_to_rgb(coul)

        if is_record:
            msg = random.choice(MSG_RECORD)
            self.lbl_msg.color = (1, 0.9, 0, 1)
        elif self.best_score > 0 and self.score >= self.best_score//2:
            msg = random.choice(MSG_HALF)
            self.lbl_msg.color = (0, 0.9, 1, 1)
        else:
            msg = random.choice(MSG_LOW)
            self.lbl_msg.color = (0.75, 0.75, 0.75, 1)

        self.lbl_crown.text      = f"👑  {self.best_score}"
        self.lbl_last.text       = f"◉  {self.last_score}"
        self.lbl_msg.text        = msg
        self.lbl_go_palier.text  = nom
        self.lbl_go_palier.color = (r, g, b, 1)

        self._show_menu(gameover=True)
        self._start_etoiles()
        Clock.schedule_interval(self._part_only, 1/60)

    def _part_only(self, dt):
        for p in self.particules[:]:
            if not p.update(dt):
                p.kill()
                self.particules.remove(p)
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha-0.035)
            self.flash_ci.a  = self.flash_alpha
        if not self.particules and self.flash_alpha <= 0:
            Clock.unschedule(self._part_only)

    # ── TOUCH ─────────────────────────────────────────────────
    def on_touch_down(self, touch):
        if self.game_state in ("menu","gameover"):
            if self.btn.collide_point(*touch.pos):
                self._on_btn()
        elif self.game_state == "playing":
            self.gravite *= -1
            self.vitesse  = 1.6*(-self.gravite)


class GravitySwitchApp(App):
    def build(self):
        Window.clearcolor = (0.03, 0, 0.09, 1)
        return Joueur()


GravitySwitchApp().run()