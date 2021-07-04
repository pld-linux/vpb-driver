#
# Conditional build:
%bcond_without  kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace package
%bcond_without	static_libs	# don't build static libraries
%bcond_with	pri		# ISDN devices support (modified libpri)

# The goal here is to have main, userspace, package built once with
# simple release number, and only rebuild kernel packages with kernel
# version as part of release number, without the need to bump release
# with every kernel change.
%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		_duplicate_files_terminate_build	0

%define		rel	7
%define		pname	vpb-driver
Summary:	Voicetronix voice processing board (VPB) driver software
Summary(pl.UTF-8):	Oprogramowanie sterowników dla kart przetwarzających głos (VPB) Voicetronix
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	4.2.58
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	LGPL v2.1+ (libraries), GPL v2+ (libpri library, kernel module)
Group:		Libraries
Source0:	http://www.voicetronix.com.au/Downloads/vpb-driver-4.x/%{pname}-%{version}.tar.gz
# Source0-md5:	f8c85b52e8d01b04d86632e98ac59d19
Patch0:		%{pname}-make.patch
Patch1:		userspace-only.patch
Patch2:		linux-4.12.patch
Patch3:		kernel-4.14.patch
Patch4:		gcc8.patch
Patch5:		kernel-5.6.patch
Patch6:		kernel-5.13.patch
URL:		http://www.voicetronix.com.au/downloads.htm#linux
BuildRequires:	rpmbuild(macros) >= 1.701
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}}
BuildRequires:	autoconf >= 2.59
BuildRequires:	libstdc++-devel
BuildRequires:	pciutils-devel
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

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-telephony-vpb\
Summary:	Linux kernel driver for Voicetronix Voice Processing Board (VPB)\
Summary(pl.UTF-8):	Sterownik jądra Linuksa do kart VPB firmy Voicetronix\
Release:	%{rel}@%{_kernel_ver_str}\
License:	GPL v2+\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-telephony-vpb\
Linux kernel driver for Voicetronix Voice Processing Board (VPB).\
\
%description -n kernel%{_alt_kernel}-telephony-vpb -l pl.UTF-8\
Sterownik jądra Linuksa do kart VPB firmy Voicetronix.\
\
%files -n kernel%{_alt_kernel}-telephony-vpb\
%defattr(644,root,root,755)\
%dir /lib/modules/%{_kernel_ver}/kernel/drivers/telephony\
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vpb.ko*\
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vtcore.ko*\
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vtopenpci.ko*\
/lib/modules/%{_kernel_ver}/kernel/drivers/telephony/vtopenswitch.ko*\
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/blunt-axe.conf\
\
%post -n kernel%{_alt_kernel}-telephony-vpb\
%depmod %{_kernel_ver}\
\
%postun -n kernel%{_alt_kernel}-telephony-vpb\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%{__make} -C src/vtcore KSRC=%{_kernelsrcdir} clean \
%{__make} -C src/vpb KSRC=%{_kernelsrcdir} clean \
%{__make} -C src/vtcore KSRC=%{_kernelsrcdir} \
%{__make} -C src/vpb KSRC=%{_kernelsrcdir} \
p=`pwd`\
%{__make} -C src/vtcore install \\\
	DESTDIR=$p/installed \\\
	KSRC=%{_kernelsrcdir}\
%{__make} -C src/vpb install \\\
	DESTDIR=$p/installed \\\
	KSRC=%{_kernelsrcdir}\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

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

%if %{with userspace}
%{__make} \
	VPATH=%{_libdir}
%endif

%{?with_kernel:%{expand:%build_kernel_packages}}

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/etc/modprobe.d
install src/libvpb/blunt-axe.conf $RPM_BUILD_ROOT/etc/modprobe.d

cp -a installed/* $RPM_BUILD_ROOT
%endif

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

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
