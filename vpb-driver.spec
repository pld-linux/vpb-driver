#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without  kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace package
%bcond_without	static_libs	# don't build static libraries
%bcond_with	pri		# ISDN devices support (modified libpri)
#
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define	rel	2
%define		pname	vpb-driver
Summary:	Voicetronix voice processing board (VPB) driver software
Summary(pl.UTF-8):	Oprogramowanie sterowników dla kart przetwarzających głos (VPB) Voicetronix
Name:		%{pname}%{_alt_kernel}
Version:	4.2.57
Release:	%{rel}
License:	LGPL v2.1+ (libraries), GPL v2+ (libpri library, kernel module)
Group:		Libraries
Source0:	http://www.voicetronix.com.au/Downloads/vpb-driver-4.x/%{pname}-%{version}.tar.gz
# Source0-md5:	35d0ea8ab7a6bda267603ca7c9b78671
Patch0:		%{pname}-make.patch
URL:		http://www.voicetronix.com.au/downloads.htm#linux
%if %{with dist_kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build
%endif
BuildRequires:	autoconf >= 2.59
BuildRequires:	libstdc++-devel
BuildRequires:	pciutils-devel
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	sed >= 4.0
BuildRequires:	zlib-devel
Requires:	vpb-libs = %{version}-%{rel}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is the Voicetronix voice processing board (VPB) driver software.

%description -l pl.UTF-8
Ten pakiet zawiera oprogramowanie sterowników kart przetwarzających
głos (VPB - voice processing board) firmy Voicetronix.

%package -n vpb-libs
Summary:	Shared VPD libraries
Summary(pl.UTF-8):	Biblioteki współdzielone VPD
License:	LGPL v2.1+
Group:		Libraries

%description -n vpb-libs
Shared VPD libraries.

%description -n vpb-libs -l pl.UTF-8
Biblioteki współdzielone VPD.

%package -n vpb-devel
Summary:	Header files for VPD libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek VPD
License:	LGPL v2.1+
Group:		Development/Libraries
Requires:	vpb-libs = %{version}-%{rel}

%description -n vpb-devel
Header files for VPD libraries.

%description -n vpb-devel -l pl.UTF-8
Pliki nagłówkowe bibliotek VPD.

%package -n vpb-static
Summary:	Static VPD libraries
Summary(pl.UTF-8):	Statyczne biblioteki VPD
License:	LGPL v2.1+
Group:		Development/Libraries
Requires:	vpb-devel = %{version}-%{rel}

%description -n vpb-static
Static VPD libraries.

%description -n vpb-static -l pl.UTF-8
Statyczne biblioteki VPD.

%package -n kernel%{_alt_kernel}-telephony-vpb
Summary:	Linux kernel driver for Voicetronix Voice Processing Board (VPB)
Summary(pl.UTF-8):	Sterownik jądra Linuksa do kart VPB firmy Voicetronix
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL v2+
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-telephony-vpb
Linux kernel driver for Voicetronix Voice Processing Board (VPB).

%description -n kernel%{_alt_kernel}-telephony-vpb -l pl.UTF-8
Sterownik jądra Linuksa do kart VPB firmy Voicetronix.

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1

%if %{without kernel}
%{__sed} -i -e 's,subdirs += $(srcdir)/vtcore $(srcdir)/vpb,,' src/Makefile.in
%endif
%if %{without userspace}
%{__sed} -i -e 's,subdirs = libtoneg libvpb utils,,' src/Makefile.in
%endif

%build
%{__aclocal}
%{__autoconf}
%if %{with userspace} && %{with static_libs}
install -d build-static
cd build-static
../%configure \
	%{?with_pri:--with-pri}
%{__make} -C src/libtoneg \
	VPATH=%{_libdir}
%{__make} -C src/libvpb \
	VPATH=%{_libdir}
cd ..
%endif
%configure \
	%{?with_pri:--with-pri} \
	--enable-shared

%if %{without userspace}
%{__make} -C src \
	%{?with_kernel:KSRC=%{_kernelsrcdir}} \
	VPATH=%{_libdir}
%else
%{__make} \
	%{?with_kernel:KSRC=%{_kernelsrcdir}} \
	VPATH=%{_libdir}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{without userspace}
%{__make} -C src install \
	DESTDIR=$RPM_BUILD_ROOT \
	%{?with_kernel:KSRC=%{_kernelsrcdir}}

install -d $RPM_BUILD_ROOT/etc/modprobe.d
install src/libvpb/blunt-axe.conf $RPM_BUILD_ROOT/etc/modprobe.d

%else

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	%{?with_kernel:KSRC=%{_kernelsrcdir}}

# let rpm generate dependencies
chmod 755 $RPM_BUILD_ROOT%{_libdir}/lib*.so*

# install man pages only for packaged software
install -d $RPM_BUILD_ROOT%{_mandir}/man1
install doc/vpbconf.1 $RPM_BUILD_ROOT%{_mandir}/man1
install doc/vpbscan.1 $RPM_BUILD_ROOT%{_mandir}/man1

%if %{with static_libs}
install build-static/src/{libtoneg/libtoneg.a,libvpb/libvpb.a} $RPM_BUILD_ROOT%{_libdir}
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n vpb-libs -p /sbin/ldconfig
%postun	-n vpb-libs -p /sbin/ldconfig

%post -n kernel%{_alt_kernel}-telephony-vpb
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-telephony-vpb
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc COPYING README README.{OpenPCI,OpenPRI,OpenSwitch12,VTCore,VpbConfig}
%attr(755,root,root) %{_sbindir}/vpbconf
%attr(755,root,root) %{_sbindir}/vpbscan
%{_datadir}/vpb-driver
%{_mandir}/man1/vpbconf.1*
%{_mandir}/man1/vpbscan.1*

%files -n vpb-libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libtoneg.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libtoneg.so.0
%attr(755,root,root) %{_libdir}/libvpb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libvpb.so.0

%files -n vpb-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libtoneg.so
%attr(755,root,root) %{_libdir}/libvpb.so
%{_includedir}/vt
%{_includedir}/vpbapi.h
%{_includedir}/vt_deprecated.h
%{_includedir}/vtcore_ioctl.h

%if %{with static_libs}
%files -n vpb-static
%defattr(644,root,root,755)
%{_libdir}/libtoneg.a
%{_libdir}/libvpb.a
%endif
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-telephony-vpb
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/kernel/drivers/telephony
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vpb.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vtcore.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vtopenpci.ko*
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vtopenswitch.ko*
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/blunt-axe.conf
%endif
